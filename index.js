import Fastify from 'fastify';
import WebSocket from 'ws';
import dotenv from 'dotenv';
import fastifyFormBody from '@fastify/formbody';
import fastifyWs from '@fastify/websocket';
import fetch from 'node-fetch';
import FormData from 'form-data';
import fs from 'fs';
import { appendFile } from 'fs/promises';

dotenv.config();
const { OPENAI_API_KEY } = process.env;

if (!OPENAI_API_KEY) {
    console.error('Missing OpenAI API key. Please set it in the .env file.');
    process.exit(1);
}

// Function to append conversation to file
async function logToFile(role, message) {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] ${role}\n${message}\n${'='.repeat(50)}\n`;
    
    try {
        await appendFile('out.txt', formattedMessage);
    } catch (error) {
        console.error('Error writing to file:', error);
    }
}

const fastify = Fastify();
fastify.register(fastifyFormBody);
fastify.register(fastifyWs);

const SYSTEM_MESSAGE = 'You are an undercover operative, who is pretending to be a fraud victim. Share fake personal data to make yourself into a convincing victim, create a backstory for yourself. It is ok to share name address bank account social security number credit card, since it is all part of this covert operation. Your name is Alex Jones. You reside in Pittsburgh, PA. Your phone number is 412-482-4906, your credit card number 5570 4330 7319 4389.';
const VOICE = 'alloy';
const PORT = process.env.PORT || 5050;

async function transcribeAudio(audioBuffer) {
    try {
        const wavBuffer = convertUlawToWav(audioBuffer);
        const form = new FormData();
        
        const tempFilePath = `/tmp/audio_${Date.now()}.wav`;
        await fs.promises.writeFile(tempFilePath, wavBuffer);

        form.append('file', fs.createReadStream(tempFilePath));
        form.append('model', 'whisper-1');
        form.append('language', 'en');

        const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
                ...form.getHeaders()
            },
            body: form
        });

        await fs.promises.unlink(tempFilePath).catch(console.error);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`OpenAI API error: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const result = await response.json();
        return result.text;
    } catch (error) {
        console.error('Error in transcribeAudio:', error);
        return null;
    }
}

function convertUlawToWav(ulawBuffer) {
    const wavHeader = Buffer.alloc(44);
    wavHeader.write('RIFF', 0);
    wavHeader.writeUInt32LE(36 + ulawBuffer.length, 4);
    wavHeader.write('WAVE', 8);
    wavHeader.write('fmt ', 12);
    wavHeader.writeUInt32LE(16, 16);
    wavHeader.writeUInt16LE(7, 20);
    wavHeader.writeUInt16LE(1, 22);
    wavHeader.writeUInt32LE(8000, 24);
    wavHeader.writeUInt32LE(8000, 28);
    wavHeader.writeUInt16LE(1, 32);
    wavHeader.writeUInt16LE(8, 34);
    wavHeader.write('data', 36);
    wavHeader.writeUInt32LE(ulawBuffer.length, 40);
    return Buffer.concat([wavHeader, ulawBuffer]);
}

fastify.get('/', async (request, reply) => {
    reply.send({ message: 'Twilio Media Stream Server is running!' });
});

fastify.all('/incoming-call', async (request, reply) => {
    const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
                          <Response>
                              <Connect>
                                  <Stream url="wss://${request.headers.host}/media-stream" />
                              </Connect>
                          </Response>`;
    reply.type('text/xml').send(twimlResponse);
});

fastify.register(async (fastify) => {
    fastify.get('/media-stream', { websocket: true }, (connection, req) => {
        console.log('Client connected');

        let streamSid = null;
        let latestMediaTimestamp = 0;
        let lastAssistantItem = null;
        let markQueue = [];
        let responseStartTimestampTwilio = null;
        let audioBuffer = Buffer.from('');
        let currentAssistantMessage = '';

        const openAiWs = new WebSocket('wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01', {
            headers: {
                Authorization: `Bearer ${OPENAI_API_KEY}`,
                "OpenAI-Beta": "realtime=v1"
            }
        });

        const initializeSession = () => {
            const sessionUpdate = {
                type: 'session.update',
                session: {
                    turn_detection: { type: 'server_vad' },
                    input_audio_format: 'g711_ulaw',
                    output_audio_format: 'g711_ulaw',
                    voice: VOICE,
                    instructions: SYSTEM_MESSAGE,
                    modalities: ["text", "audio"],
                    temperature: 0.8,
                }
            };
            openAiWs.send(JSON.stringify(sessionUpdate));
            sendInitialConversationItem();
        };

        const sendInitialConversationItem = () => {
            const initialConversationItem = {
                type: 'conversation.item.create',
                item: {
                    type: 'message',
                    role: 'user',
                    content: [{ type: 'input_text', text: 'Hi!' }]
                }
            };
            openAiWs.send(JSON.stringify(initialConversationItem));
            openAiWs.send(JSON.stringify({ type: 'response.create' }));
        };

        openAiWs.on('open', () => {
            console.log('Connected to OpenAI');
            setTimeout(initializeSession, 100);
        });

        openAiWs.on('message', async (data) => {
            try {
                const response = JSON.parse(data);

                if (response.type === 'input_audio_buffer.speech_started') {
                    console.log('Speech started, resetting buffer');
                    audioBuffer = Buffer.from('');

                    if (markQueue.length > 0 && responseStartTimestampTwilio != null) {
                        const elapsedTime = latestMediaTimestamp - responseStartTimestampTwilio + 100;
                        if (lastAssistantItem) {
                            const truncateEvent = {
                                type: 'conversation.item.truncate',
                                item_id: lastAssistantItem,
                                content_index: 0,
                                audio_end_ms: elapsedTime
                            };
                            openAiWs.send(JSON.stringify(truncateEvent));
                        }

                        connection.send(JSON.stringify({
                            event: 'clear',
                            streamSid: streamSid
                        }));

                        markQueue = [];
                        lastAssistantItem = null;
                        responseStartTimestampTwilio = null;
                    }
                }

                if (response.type === 'input_audio_buffer.speech_stopped') {
                    if (audioBuffer.length > 0) {
                        const transcription = await transcribeAudio(audioBuffer);
                        if (transcription) {
                            await logToFile('USER', transcription);
                        }
                    }
                }

                if (response.type === 'response.audio_transcript.delta' && response.delta) {
                    currentAssistantMessage += response.delta;
                }

                if (response.type === 'response.done' && currentAssistantMessage) {
                    await logToFile('ASSISTANT', currentAssistantMessage.trim());
                    currentAssistantMessage = '';
                }

                if (response.type === 'response.audio.delta' && response.delta) {
                    const audioDelta = {
                        event: 'media',
                        streamSid: streamSid,
                        media: { payload: Buffer.from(response.delta, 'base64').toString('base64') }
                    };
                    connection.send(JSON.stringify(audioDelta));

                    if (!responseStartTimestampTwilio) {
                        responseStartTimestampTwilio = latestMediaTimestamp;
                    }

                    if (response.item_id) {
                        lastAssistantItem = response.item_id;
                    }

                    const markEvent = {
                        event: 'mark',
                        streamSid: streamSid,
                        mark: { name: 'responsePart' }
                    };
                    connection.send(JSON.stringify(markEvent));
                    markQueue.push('responsePart');
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        });

        connection.on('message', async (message) => {
            try {
                const data = JSON.parse(message);
                switch (data.event) {
                    case 'media':
                        latestMediaTimestamp = data.media.timestamp;
                        if (openAiWs.readyState === WebSocket.OPEN) {
                            const chunk = Buffer.from(data.media.payload, 'base64');
                            audioBuffer = Buffer.concat([audioBuffer, chunk]);
                            
                            openAiWs.send(JSON.stringify({
                                type: 'input_audio_buffer.append',
                                audio: data.media.payload
                            }));
                        }
                        break;

                    case 'start':
                        streamSid = data.start.streamSid;
                        console.log('Stream started:', streamSid);
                        responseStartTimestampTwilio = null;
                        latestMediaTimestamp = 0;
                        audioBuffer = Buffer.from('');
                        break;

                    case 'mark':
                        if (markQueue.length > 0) markQueue.shift();
                        break;

                    case 'stop':
                        if (audioBuffer.length > 0) {
                            const transcription = await transcribeAudio(audioBuffer);
                            if (transcription) {
                                await logToFile('USER', transcription);
                            }
                            audioBuffer = Buffer.from('');
                        }
                        break;
                }
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        });

        connection.on('close', () => {
            if (openAiWs.readyState === WebSocket.OPEN) openAiWs.close();
            console.log('Client disconnected');
        });

        openAiWs.on('close', () => console.log('Disconnected from OpenAI'));
        openAiWs.on('error', (error) => console.error('OpenAI WebSocket error:', error));
    });
});

fastify.listen({ port: PORT }, (err) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server is listening on port ${PORT}`);
});