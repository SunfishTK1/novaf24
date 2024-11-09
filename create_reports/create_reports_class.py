from openai import OpenAI, AsyncOpenAI

from typing import Dict

import json
import os
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.graphics.shapes import Drawing, Circle, Line, Rect
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

load_dotenv()

LIKELIHOOD_OF_SCAM_RATINGS = {
    'very high': 1,
    'high': 2,
    'medium': 3,
    'low': 4,
    'very low': 5
}

def get_color(numerical_rating: int) -> colors.Color:
    """
    Maps the numerical rating to a color from dark red to dark green.
    
    Parameters:
    - numerical_rating (int): The numerical rating (1 to 5).
    
    Returns:
    - colors.Color: The corresponding color.
    """
    color_map = {
        1: colors.HexColor("#8B0000"),  # Dark Red
        2: colors.HexColor("#B22222"),  # Firebrick
        3: colors.HexColor("#FFA500"),  # Orange
        4: colors.HexColor("#9ACD32"),  # YellowGreen
        5: colors.HexColor("#006400")   # Dark Green
    }
    return color_map.get(numerical_rating, colors.HexColor("#808080"))  # Default Grey

class ConversationReport:
    def __init__(self, transcript: str, *args, **kwargs):
        self.transcript = transcript
        self.client = OpenAI()

        self.executive_summary = kwargs.get('executive_summary', '')
        self.introduction = kwargs.get('introduction', '')
        self.likelihood_of_scam = kwargs.get('likelihood_of_scam', '')
        self.call_center_location_analysis = kwargs.get('call_center_location_analysis', '')
        self.impersonation_tactics = kwargs.get('impersonation_tactics', '')
        self.technology_utilization = kwargs.get('technology_utilization', '')
        self.scam_workflow_analysis = kwargs.get('scam_workflow_analysis', '')
        self.risk_assessment = kwargs.get('risk_assessment', '')
        self.mitigation_strategies = kwargs.get('mitigation_strategies', '')
        self.conclusion = kwargs.get('conclusion', '')
        self.appendices = kwargs.get('appendices', '')
        self.additional_considerations = kwargs.get('additional_considerations', '')
        self.number_rating_likelihood_of_scam = 0

    def set_executive_summary(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Executive Summary section.

        Parameters:
        - paragraph (str): Content for the Executive Summary.

        Returns:
        - Dict[str, str]: Subtitle and details for the Executive Summary.
        """
        self.executive_summary = {
            "subtitle": "Executive Summary",
            "details": paragraph
        }
        return self.executive_summary

    def set_introduction(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Introduction section.

        Parameters:
        - paragraph (str): Content for the Introduction.

        Returns:
        - Dict[str, str]: Subtitle and details for the Introduction.
        """
        self.introduction = {
            "subtitle": "Introduction",
            "details": paragraph
        }
        return self.introduction
    
    def set_likelihood_of_scam(self, rating: str, rationale: str) -> Dict[str, str]:
        """
        Sets the Likelihood of Scam section.

        Parameters:
        - rating (str): The likelihood rating (e.g., "high", "medium").
        - rationale (str): A one-sentence rationale for the rating.

        Returns:
        - Dict[str, str]: Subtitle and details for the Likelihood of Scam.
        """
        numerical_rating = LIKELIHOOD_OF_SCAM_RATINGS.get(rating.lower(), 3)
        self.likelihood_of_scam = {
            "subtitle": "Likelihood of Scam",
            "details": f"Rating: {rating.capitalize()} ({numerical_rating}/5)\nRationale: {rationale}"
        }
        self.number_rating_likelihood_of_scam = numerical_rating
        return self.likelihood_of_scam

    '''
    def set_likelihood_of_scam(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Likelihood of Scam section.

        Parameters:
        - paragraph (str): Content for the Likelihood of Scam.

        Returns:
        - Dict[str, str]: Subtitle and details for the Likelihood of Scam.
        """
        self.likelihood_of_scam = {
            "subtitle": "Likelihood of Scam",
            "details": paragraph
        }
        return self.likelihood_of_scam
    '''

    def set_call_center_location_analysis(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Call Center Location Analysis section.

        Parameters:
        - paragraph (str): Content for the Call Center Location Analysis.

        Returns:
        - Dict[str, str]: Subtitle and details for the Call Center Location Analysis.
        """
        self.call_center_location_analysis = {
            "subtitle": "Call Center Location Analysis",
            "details": paragraph
        }
        return self.call_center_location_analysis

    def set_impersonation_tactics(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Impersonation Tactics section.

        Parameters:
        - paragraph (str): Content for the Impersonation Tactics.

        Returns:
        - Dict[str, str]: Subtitle and details for the Impersonation Tactics.
        """
        self.impersonation_tactics = {
            "subtitle": "Impersonation Tactics",
            "details": paragraph
        }
        return self.impersonation_tactics

    def set_technology_utilization(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Technology Utilization section.

        Parameters:
        - paragraph (str): Content for the Technology Utilization.

        Returns:
        - Dict[str, str]: Subtitle and details for the Technology Utilization.
        """
        self.technology_utilization = {
            "subtitle": "Technology Utilization",
            "details": paragraph
        }
        return self.technology_utilization

    def set_scam_workflow_analysis(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Scam Workflow Analysis section.

        Parameters:
        - paragraph (str): Content for the Scam Workflow Analysis.

        Returns:
        - Dict[str, str]: Subtitle and details for the Scam Workflow Analysis.
        """
        self.scam_workflow_analysis = {
            "subtitle": "Scam Workflow Analysis",
            "details": paragraph
        }
        return self.scam_workflow_analysis

    def set_risk_assessment(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Risk Assessment section.

        Parameters:
        - paragraph (str): Content for the Risk Assessment.

        Returns:
        - Dict[str, str]: Subtitle and details for the Risk Assessment.
        """
        self.risk_assessment = {
            "subtitle": "Risk Assessment",
            "details": paragraph
        }
        return self.risk_assessment

    def set_mitigation_strategies(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Mitigation Strategies section.

        Parameters:
        - paragraph (str): Content for the Mitigation Strategies.

        Returns:
        - Dict[str, str]: Subtitle and details for the Mitigation Strategies.
        """
        self.mitigation_strategies = {
            "subtitle": "Mitigation Strategies",
            "details": paragraph
        }
        return self.mitigation_strategies

    def set_conclusion(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Conclusion section.

        Parameters:
        - paragraph (str): Content for the Conclusion.

        Returns:
        - Dict[str, str]: Subtitle and details for the Conclusion.
        """
        self.conclusion = {
            "subtitle": "Conclusion",
            "details": paragraph
        }
        return self.conclusion

    def set_appendices(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Appendices section.

        Parameters:
        - paragraph (str): Content for the Appendices.

        Returns:
        - Dict[str, str]: Subtitle and details for the Appendices.
        """
        self.appendices = {
            "subtitle": "Appendices",
            "details": paragraph
        }
        return self.appendices

    def set_additional_considerations(self, paragraph: str) -> Dict[str, str]:
        """
        Sets the Additional Considerations section.

        Parameters:
        - paragraph (str): Content for the Additional Considerations.

        Returns:
        - Dict[str, str]: Subtitle and details for the Additional Considerations.
        """
        self.additional_considerations = {
            "subtitle": "Additional Considerations",
            "details": paragraph
        }
        return self.additional_considerations

    def generate_report_data(self) -> Dict[str, Dict[str, str]]:
        """
        Compiles all sections into a full report.

        Returns:
        - Dict[str, Dict[str, str]]: Complete report with all sections.
        """
        return {
            "Executive Summary": self.executive_summary,
            "Introduction": self.introduction,
            "Likelihood of Scam": self.likelihood_of_scam,
            "Call Center Location Analysis": self.call_center_location_analysis,
            "Impersonation Tactics": self.impersonation_tactics,
            "Technology Utilization": self.technology_utilization,
            "Scam Workflow Analysis": self.scam_workflow_analysis,
            "Risk Assessment": self.risk_assessment,
            "Mitigation Strategies": self.mitigation_strategies,
            "Conclusion": self.conclusion,
            "Appendices": self.appendices,
            "Additional Considerations": self.additional_considerations
        }
    
    def generate_full_boring_report(self, output_file: str):
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(output_file, pagesize=letter)
        story = []

        sections = {
            "Executive Summary": self.executive_summary,
            "Introduction": self.introduction,
            "Likelihood of Scam": self.likelihood_of_scam,
            "Call Center Location Analysis": self.call_center_location_analysis,
            "Impersonation Tactics": self.impersonation_tactics,
            "Technology Utilization": self.technology_utilization,
            "Scam Workflow Analysis": self.scam_workflow_analysis,
            "Risk Assessment": self.risk_assessment,
            "Mitigation Strategies": self.mitigation_strategies,
            "Conclusion": self.conclusion,
            "Appendices": self.appendices,
            "Additional Considerations": self.additional_considerations
        }

        for section_title, content in sections.items():
            story.append(Paragraph(f"<strong>{section_title}</strong>", styles['Heading1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(content.get("details", ""), styles['BodyText']))
            story.append(Spacer(1, 24))

        doc.build(story)

    def generate_full_report(self, output_file: str):
        # Retrieve the sample stylesheet
        styles = getSampleStyleSheet()
        
        # Modify the existing 'BodyText' style instead of adding a new one
        styles['BodyText'].fontSize = 12
        styles['BodyText'].leading = 16
        styles['BodyText'].spaceAfter = 12
        styles['BodyText'].textColor = colors.HexColor("#2C3E50")
        styles['BodyText'].alignment = TA_JUSTIFY
        styles['BodyText'].fontName = 'Helvetica'
        
        # Add new styles for other elements
        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontSize=36,
            leading=42,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#34495E"),
            spaceAfter=40,
            fontName='Helvetica'
        ))
        styles.add(ParagraphStyle(
            name='SectionHeading',
            fontSize=20,
            leading=24,
            spaceAfter=10,
            textColor=colors.HexColor("#2980B9"),
            fontName='Helvetica-Bold'
        ))
        styles.add(ParagraphStyle(
            name='Footer',
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#95A5A6"),
            fontName='Helvetica'
        ))
        
        # Create the PDF document with a custom page template
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )
        
        # Story is the list of flowables
        story = []
        
        # ======= Cover Page =======
        def add_cover_page(story, styles):
            # Add a large spacer to push content to the center
            story.append(Spacer(1, 3 * inch))
            
            # Title
            title = "Scam Call Analysis Report"
            story.append(Paragraph(title, styles['CoverTitle']))
            
            # Subtitle
            subtitle = "Comprehensive Analysis and Mitigation Strategies"
            story.append(Paragraph(subtitle, styles['CoverSubtitle']))
            
            # Optional: Add a logo or image
            # Uncomment and provide the path to your logo image
            # try:
            #     logo = Image("path_to_logo.png")
            #     logo.drawHeight = 1 * inch
            #     logo.drawWidth = 1 * inch
            #     logo.hAlign = 'CENTER'
            #     story.append(logo)
            # except Exception as e:
            #     print(f"Logo image not found: {e}")
            
            # Add page break after cover
            story.append(PageBreak())
        
        add_cover_page(story, styles)
        
        # ======= Report Sections =======
        sections = self.generate_report_data()
        
        for section_title, content in sections.items():
            # Add a section heading with decorative line
            story.append(Paragraph(section_title, styles['SectionHeading']))
            story.append(Spacer(1, 6))
            
            # Add a colored box around the section
            box_color = colors.HexColor("#ECF0F1")  # Light grey-blue background
            box_padding = 10
            
            # Handle Likelihood of Scam separately
            section_details = content.get("details", "") if isinstance(content, dict) else content
            if section_title == "Likelihood of Scam" and isinstance(content, dict):
                # Create a colored dot for the rating
                dot_color = get_color(self.number_rating_likelihood_of_scam)
                drawing = Drawing(10, 10)
                drawing.add(Circle(5, 5, 4, fillColor=dot_color, strokeColor=dot_color))
        
                # Create a table with the dot and the details
                table = Table(
                    [[drawing, Paragraph(content.get("details", ""), styles['BodyText'])]],
                    colWidths=[20, 450],
                    style=TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('BACKGROUND', (0,0), (-1,-1), box_color),
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BDC3C7")),
                        ('ROUNDING', (0,0), (-1,-1), 4),
                    ])
                )
                story.append(table)
            else:
                # Wrap the section details in a colored box
                box_table = Table(
                    [[Paragraph(section_details, styles['BodyText'])]],
                    colWidths=[doc.width],
                    style=TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), box_color),
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BDC3C7")),
                        ('ROUNDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), box_padding),
                        ('RIGHTPADDING', (0, 0), (-1, -1), box_padding),
                        ('TOPPADDING', (0, 0), (-1, -1), box_padding),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), box_padding),
                    ])
                )
                story.append(box_table)
            
            # Add some space after each section
            story.append(Spacer(1, 12))
            
            # Optional: Add a decorative line or shape after each section
            # Here, we add a simple line
            line = Line(0, 0, doc.width, 0)
            line.strokeColor = colors.HexColor("#95A5A6")
            line.strokeWidth = 1
            drawing = Drawing(doc.width, 1)
            drawing.add(line)
            story.append(drawing)
            story.append(Spacer(1, 24))
        
        # ======= Footer and Page Numbers =======
        def add_page_number(canvas_obj, doc):
            page_num = canvas_obj.getPageNumber()
            text = f"Page {page_num}"
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.setFillColor(colors.HexColor("#95A5A6"))
            canvas_obj.drawCentredString(letter[0] / 2.0, 1 * cm, text)
        
        # ======= Build the PDF =======
        doc.build(
            story,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number
        )



    def generate_report(self):
        # TODO: Use OpenAI API and models to create a report with function calling

        pass

    def analyze_transcript_with_gpt(self) -> None:
        """
        Analyzes the transcript using GPT-4 and automatically populates all report sections
        using tool calling functionality.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "set_executive_summary",
                    "description": "Set the executive summary of the report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Executive Summary section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_introduction",
                    "description": "Set the introduction section of the report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Introduction section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_likelihood_of_scam",
                    "description": "Set the likelihood of scam analysis section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rating": {
                                "type": "string",
                                "enum": ["very high", "high", "medium", "low", "very low"],
                                "description": "The likelihood rating of the scam."
                            },
                            "rationale": {
                                "type": "string",
                                "description": "A one-sentence rationale for the rating."
                            }
                        },
                        "required": ["rating", "rationale"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_call_center_location_analysis",
                    "description": "Set the call center location analysis section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Call Center Location Analysis section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_impersonation_tactics",
                    "description": "Set the impersonation tactics section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Impersonation Tactics section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_technology_utilization",
                    "description": "Set the technology utilization section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Technology Utilization section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_scam_workflow_analysis",
                    "description": "Set the scam workflow analysis section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Scam Workflow Analysis section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_risk_assessment",
                    "description": "Set the risk assessment section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Risk Assessment section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_mitigation_strategies",
                    "description": "Set the mitigation strategies section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Mitigation Strategies section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_conclusion",
                    "description": "Set the conclusion section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Conclusion section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_appendices",
                    "description": "Set the appendices section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Appendices section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_additional_considerations",
                    "description": "Set the additional considerations section",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paragraph": {
                                "type": "string",
                                "description": "Content for the Additional Considerations section"
                            }
                        },
                        "required": ["paragraph"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing potential scam calls and creating detailed reports. Analyze the provided transcript and populate each section of the report using the available tools. Be thorough and professional in your analysis."
            },
            {
                "role": "user",
                "content": f"Please analyze this transcript and populate all sections of the report: {self.transcript}"
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # Process tool calls if any
            if message.tool_calls:
                messages.append(message)
                
                # Handle each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the corresponding class method
                    if hasattr(self, function_name):
                        function = getattr(self, function_name)
                        function_response = function(**function_args)
                        
                        # Add the function response to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response)
                        })

                # Get final response after tool calls
                final_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )

        except Exception as e:
            print(f"Error during transcript analysis: {str(e)}")
            raise



if __name__ == "__main__":
    # Sample transcript and data for testing
    sample_transcript = "This is a sample transcript of a conversation."
    sample_data = {
        "executive_summary": "This is the executive summary.",
        "introduction": "This is the introduction.",
        "likelihood_of_scam": "High likelihood of scam.",
        "call_center_location_analysis": "The call center is likely located in XYZ.",
        "impersonation_tactics": "They are pretending to be ABC.",
        "technology_utilization": "They are using XYZ technology.",
        "scam_workflow_analysis": "The scam works as follows...",
        "risk_assessment": "The risk is assessed as high.",
        "mitigation_strategies": "The following strategies can mitigate the risk...",
        "conclusion": "In conclusion...",
        "appendices": "Appendix A, Appendix B...",
        "additional_considerations": "Additional considerations include..."
    }

    t_text = '''
            [Phone rings]
        [Call connects]
        Scammer: Hello, this is Michael Wilson from the Social Security Administration. I'm calling regarding suspicious activity on your social security number. Who am I speaking with?
        Victim: This is Margaret Johnson. What's wrong with my social security?
        Scammer: Ma'am, we've detected multiple suspicious transactions linked to your social security number in Texas. Several bank accounts were opened using your information, and there are connections to drug trafficking. Have you been to Texas recently?
        Victim: No, I haven't! Oh my goodness, I've never been to Texas. This must be a mistake!
        Scammer: Ma'am, please remain calm. I understand this is concerning. We can help resolve this, but I need to verify your identity first. Could you confirm your social security number for me?
        Victim: Well... I'm not sure if I should give that out over the phone...
        Scammer: Mrs. Johnson, I understand your concern, but this is a federal investigation. If we can't verify your identity, we'll have to freeze all your accounts immediately and issue an arrest warrant. We're trying to help you here.
        Victim: An arrest warrant? But I haven't done anything wrong! I... okay, my number is...
        Scammer: Yes, go ahead. This is a secure line.
        Victim: It's 483-...
        [Phone rings in background]
        Victim: Oh, that's my other line. My daughter's calling...
        Scammer: Ma'am, please don't hang up. This is a federal investigation. If you disconnect, we'll have to proceed with immediate legal action.
        Victim: I should probably check with my daughter first...
        Scammer: Mrs. Johnson, you cannot discuss this with anyone. This is a federal investigation under Section 411 of the SSA code. Any disclosure could result in immediate arrest.
        [Sound of other phone continuing to ring]
        Victim: I'm sorry, but something doesn't feel right about this. I'm going to call the Social Security office directly.
        Scammer: [Breaking character slightly] Ma'am, if you hang up now, you'll be arrested within the hour! This is your final warning—
        [Call ends]
        '''
            
    report = ConversationReport(transcript=t_text)
    report.analyze_transcript_with_gpt()
    report.generate_full_report("output.pdf")
    
    # Create an instance of ConversationReport
    #report = ConversationReport(sample_transcript, **sample_data)

    # Generate the PDF report
    #output_file = "sample_report.pdf"
    #report.generate_full_report(output_file)

    #print(f"Report generated and saved to {output_file}")