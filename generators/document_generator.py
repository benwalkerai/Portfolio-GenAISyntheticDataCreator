"""Document generation for Word, PDF, and text formats."""

import io
import tempfile
from typing import Dict, List, Tuple, Any, Optional
from docx import Document
from docx.shared import Inches

# Try to import reportlab, with fallback
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("  Warning: ReportLab not installed. PDF generation will be disabled.")


class DocumentGenerator:
    """Generate document content and format output files."""
    
    def __init__(self, data_generator: Any) -> None:
        """
        Initialize the document generator with LLM access.
        
        Args:
            data_generator: The main data generator instance providing LLM access
        """
        self.data_generator = data_generator
        
    def clear_cache(self) -> None:
        """
        Clear all cached document generation data.
        
        This method should be called before each new document generation to ensure
        fresh, unique content is created.
        """
        # DocumentGenerator doesn't have a cache dict currently, but add for consistency
        # and future-proofing in case caching is added later
        if hasattr(self, 'llm_cache'):
            self.llm_cache.clear()
        print(" DocumentGenerator cache cleared")

    def generate_document_content(
        self, 
        content_type: str, 
        pages: int, 
        subject: str
    ) -> str:
        """
        Generate document content using a single LLM call for shorter documents.
        
        This method uses a single comprehensive prompt to generate the entire
        document content. It's optimized for shorter documents (1-2 pages) where
        a single LLM call can produce sufficient content.
        
        Args:
            content_type (str): Type of document to generate. Must be one of:
                - "whitepaper": Technical analysis and methodology
                - "article": In-depth analysis with case studies
                - "report": Business analysis with strategic recommendations
                - "proposal": Project proposals with timelines and budgets
                - "design": IT system design and architecture documents
            pages (int): Target number of pages for the document
            subject (str): Subject/topic for the document content
        
        Returns:
            str: Generated document content with proper structure and formatting
        
        Raises:
            ValueError: If content_type is not supported
        
        Example:
            >>> content = doc_gen.generate_document_content(
            ...     "article", 2, "Machine Learning in Healthcare"
            ... )
            >>> print(f"Generated {len(content.split())} words")
        """
        target_words = pages * 275
        
        prompts = {
            "whitepaper": f"""Write a comprehensive technical whitepaper on {subject} that is EXACTLY {pages} pages long (approximately {target_words} words).

STRUCTURE REQUIREMENTS:
- Page 1: Executive Summary (1 full page)
- Page 2: Introduction and Background (1 full page)
{f"- Pages 3-{pages-2}: Technical Analysis, Methodology, Implementation Details ({pages-4} pages)" if pages > 4 else ""}
{f"- Page {pages-1}: Findings and Results (1 full page)" if pages > 3 else ""}
- Page {pages}: Conclusions and References (1 full page)

CONTENT REQUIREMENTS:
- Write detailed paragraphs with 4-6 sentences each
- Include specific technical details and examples
- Add subsections with descriptive headings
- Ensure each section is substantive and detailed
- The document must be exactly {pages} pages when printed
- Target approximately {target_words} total words

Make it detailed, professional, and comprehensive. Note at the end that this is synthetically created data.""",

            "article": f"""Write a detailed article about {subject} that is EXACTLY {pages} pages long (approximately {target_words} words).

STRUCTURE REQUIREMENTS:
- Page 1: Introduction and overview
{f"- Pages 2-{pages-1}: Main content with multiple detailed sections ({pages-2} pages)" if pages > 2 else ""}
- Page {pages}: Conclusion and key takeaways

CONTENT REQUIREMENTS:
- Write in-depth paragraphs with 5-7 sentences each
- Include practical examples and case studies
- Add multiple subsections with detailed explanations
- Use bullet points and numbered lists where appropriate
- The article must be exactly {pages} pages when printed
- Target approximately {target_words} total words

Include multiple sections, subsections, and practical examples. Note at the end that this is synthetically created data.""",

            "report": f"""Write a comprehensive business report on {subject} that is EXACTLY {pages} pages long (approximately {target_words} words).

STRUCTURE REQUIREMENTS:
- Page 1: Executive Summary and Key Findings
- Page 2: Introduction and Methodology
{f"- Pages 3-{pages-2}: Detailed Analysis and Data ({pages-4} pages)" if pages > 4 else ""}
{f"- Page {pages-1}: Strategic Recommendations (1 full page)" if pages > 3 else ""}
- Page {pages}: Conclusions and Next Steps

CONTENT REQUIREMENTS:
- Include detailed data analysis descriptions
- Add charts and graphs descriptions (describe what they would show)
- Write comprehensive strategic recommendations
- Include market analysis and competitive landscape
- The report must be exactly {pages} pages when printed
- Target approximately {target_words} total words

Make it detailed and professional with strategic recommendations. Note at the end that this is synthetically created data.""",

            "proposal": f"""Write a detailed project proposal for {subject} that is EXACTLY {pages} pages long (approximately {target_words} words).

STRUCTURE REQUIREMENTS:
- Page 1: Project Overview and Objectives
- Page 2: Detailed Scope and Requirements
{f"- Page 3: Timeline and Milestones" if pages > 3 else ""}
{f"- Page 4: Budget and Resource Allocation" if pages > 4 else ""}
{f"- Pages {5 if pages > 4 else 3}-{pages-1}: Implementation Plan and Risk Analysis" if pages > 4 else ""}
- Page {pages}: Expected Outcomes and Success Metrics

CONTENT REQUIREMENTS:
- Detailed project scope with specific deliverables
- Comprehensive timeline with multiple phases
- Detailed budget breakdown with justifications
- Risk analysis with mitigation strategies
- The proposal must be exactly {pages} pages when printed
- Target approximately {target_words} total words

Include scope, timeline, budget considerations and risk analysis. Note at the end that this is synthetically created data.""",

            "design": f"""Write a detailed design document for an IT project on {subject} that is EXACTLY {pages} pages long (approximately {target_words} words).

STRUCTURE REQUIREMENTS:
- Page 1: System Overview and Architecture
- Page 2: Technical Requirements and Components
{f"- Page 3: Interface Design and Data Flow" if pages > 3 else ""}
{f"- Page 4: Security and Performance Considerations" if pages > 4 else ""}
{f"- Pages {5 if pages > 4 else 3}-{pages-1}: Implementation Details and Testing" if pages > 4 else ""}
- Page {pages}: Deployment and Maintenance

CONTENT REQUIREMENTS:
- Detailed system architecture descriptions
- Technical component specifications
- Interface design with specific examples
- Data flow diagrams descriptions
- Security protocols and performance metrics
- The document must be exactly {pages} pages when printed
- Target approximately {target_words} total words

Include architecture, components, interfaces and data flow. Note at the end that this is synthetically created data."""
        }

        if content_type not in prompts:
            raise ValueError(f"Invalid content type: {content_type}. Choose from {list(prompts.keys())}.")

        prompt = prompts.get(content_type)
        
        # Use a professional writing system prompt
        system_prompt = "You are a professional technical writer and document specialist. Write clear, well-structured content in plain text with Markdown formatting. Do NOT output JSON or wrap content in code blocks. Focus on high-quality, readable content."
        
        return self.data_generator.generate_with_ollama(prompt, max_tokens=6000, system_prompt=system_prompt)

    def generate_document_content_iterative(
        self, 
        content_type: str, 
        pages: int, 
        subject: str
    ) -> str:
        """
        Generate document content by building it section by section for longer documents.
        
        This method uses an iterative approach where each section is generated
        separately using focused prompts. This ensures better quality and length
        control for longer documents (3+ pages) by breaking down the generation
        process into manageable sections.
        
        Args:
            content_type (str): Type of document to generate. Must be one of:
                - "whitepaper": Technical analysis and methodology
                - "article": In-depth analysis with case studies
                - "report": Business analysis with strategic recommendations
                - "proposal": Project proposals with timelines and budgets
                - "design": IT system design and architecture documents
            pages (int): Target number of pages for the document
            subject (str): Subject/topic for the document content
        
        Returns:
            str: Generated document content with proper structure and formatting
        
        Example:
            >>> content = doc_gen.generate_document_content_iterative(
            ...     "whitepaper", 8, "Quantum Computing Applications"
            ... )
            >>> print(f"Generated {len(content.split())} words")
        """
        print(f"🔄 Generating {pages}-page {content_type} iteratively...")
        sections: List[str] = []
        
        # Section configurations for different document types
        section_configs = {
            "whitepaper": [
                ("Executive Summary", "Write a comprehensive 1-page executive summary with key findings and recommendations"),
                ("Introduction and Background", "Write a detailed introduction covering the background, context, and importance of the topic"),
                ("Technical Analysis", "Write an in-depth technical analysis section with detailed explanations and technical specifications"),
                ("Methodology", "Write a detailed methodology section explaining approaches, frameworks, and implementation strategies"),
                ("Implementation Details", "Write comprehensive implementation details including step-by-step processes and technical requirements"),
                ("Results and Findings", "Write detailed results and findings with data analysis and performance metrics"),
                ("Future Considerations", "Write about future implications, scalability, and evolution of the technology"),
                ("Conclusions and References", "Write comprehensive conclusions with actionable recommendations and references")
            ],
            "article": [
                ("Introduction", "Write a comprehensive introduction that sets the context and engages the reader"),
                ("Main Analysis", "Write the main analysis section with detailed content and thorough examination"),
                ("Case Studies and Examples", "Write detailed case studies and real-world examples with specific scenarios"),
                ("Industry Impact and Implications", "Write about industry impact, market implications, and economic effects"),
                ("Current Trends and Developments", "Write about current trends, recent developments, and emerging patterns"),
                ("Best Practices and Recommendations", "Write about best practices, recommendations, and actionable insights"),
                ("Future Outlook", "Write about future trends, predictions, and long-term implications"),
                ("Conclusion", "Write a comprehensive conclusion that summarizes key points and provides final thoughts")
            ],
            "report": [
                ("Executive Summary", "Write an executive summary with key findings, recommendations, and critical insights"),
                ("Introduction and Methodology", "Write introduction covering scope, objectives, and detailed methodology"),
                ("Market Analysis", "Write detailed market analysis including size, trends, competitors, and opportunities"),
                ("Data Analysis and Insights", "Write comprehensive data analysis with statistical insights and interpretations"),
                ("Strategic Recommendations", "Write strategic recommendations with detailed implementation guidance"),
                ("Risk Assessment", "Write thorough risk assessment including potential challenges and mitigation strategies"),
                ("Implementation Plan", "Write detailed implementation plan with timelines, resources, and success metrics"),
                ("Financial Analysis", "Write financial analysis including costs, benefits, and ROI projections"),
                ("Conclusions and Next Steps", "Write conclusions with clear next steps and action items")
            ],
            "proposal": [
                ("Project Overview and Objectives", "Write project overview covering goals, scope, and strategic alignment"),
                ("Scope and Requirements", "Write detailed scope definition and comprehensive requirements analysis"),
                ("Timeline and Milestones", "Write comprehensive timeline with detailed milestones and deliverable schedules"),
                ("Budget and Resource Allocation", "Write detailed budget breakdown and resource allocation plans"),
                ("Implementation Strategy", "Write implementation strategy with detailed methodology and approach"),
                ("Risk Analysis and Mitigation", "Write comprehensive risk analysis with detailed mitigation strategies"),
                ("Team and Expertise", "Write about team composition, expertise, and organizational capabilities"),
                ("Quality Assurance", "Write about quality assurance processes, testing, and validation procedures"),
                ("Expected Outcomes and Success Metrics", "Write about expected outcomes, success criteria, and measurement methods")
            ],
            "design": [
                ("System Overview and Architecture", "Write system overview covering high-level architecture and design principles"),
                ("Technical Requirements", "Write detailed technical requirements including functional and non-functional specifications"),
                ("Interface Design and User Experience", "Write about interface design, user experience, and interaction patterns"),
                ("Data Architecture and Flow", "Write about data architecture, database design, and information flow"),
                ("Security and Performance", "Write about security considerations, performance requirements, and scalability"),
                ("Implementation Details", "Write detailed implementation specifications including technologies and frameworks"),
                ("Testing and Quality Assurance", "Write about testing strategies, quality assurance processes, and validation methods"),
                ("Deployment and Infrastructure", "Write about deployment architecture, infrastructure requirements, and operational considerations"),
                ("Maintenance and Support", "Write about maintenance procedures, support processes, and long-term sustainability")
            ]
        }
        
        # Get sections for this document type
        all_sections = section_configs.get(content_type, section_configs["article"])
        
        # Calculate sections to use based on page count
        sections_to_use = min(len(all_sections), max(pages, 3))
        selected_sections = all_sections[:sections_to_use]
        
        # If we need more sections for very long documents, add additional analysis sections
        while len(selected_sections) < pages:
            additional_sections = [
                ("Additional Technical Analysis", "Write additional detailed technical analysis with deeper insights"),
                ("Supplementary Research", "Write supplementary research findings and supporting evidence"),
                ("Extended Case Studies", "Write extended case studies with more detailed examples"),
                ("Advanced Considerations", "Write about advanced considerations and complex scenarios")
            ]
            selected_sections.extend(additional_sections[:pages - len(selected_sections)])
        
        # Calculate words per section (aim for more words to ensure length)
        total_target_words = pages * 300  # Slightly higher target
        words_per_section = total_target_words // len(selected_sections)
        
        # Generate each section
        for i, (section_title, section_instruction) in enumerate(selected_sections):
            section_prompt = f"""{section_instruction} for a {content_type} about {subject}.

REQUIREMENTS:
- Write approximately {words_per_section} words for this section
- Include detailed explanations with specific examples related to {subject}
- Use professional, technical language appropriate for the topic
- Make this section substantial and comprehensive with multiple paragraphs
- Include subsections, bullet points, and numbered lists where appropriate
- Provide concrete examples and detailed analysis
- This is section {i+1} of {len(selected_sections)} in a {pages}-page document

Topic: {subject}
Document Type: {content_type}
Section: {section_title}

Write detailed, professional content that thoroughly covers this section with substantial depth and analysis."""

            print(f" Generating section {i+1}/{len(selected_sections)}: {section_title}")
            
            # Use a professional writing system prompt
            system_prompt = "You are a professional technical writer and document specialist. Write clear, well-structured content in plain text with Markdown formatting. Do NOT output JSON or wrap content in code blocks. Focus on high-quality, readable content."
            
            section_content = self.data_generator.generate_with_ollama(section_prompt, max_tokens=2000, system_prompt=system_prompt)
            
            # Add section to document with proper formatting
            formatted_section = f"# {section_title}\n\n{section_content}"
            sections.append(formatted_section)
        
        # Add final disclaimer
        final_note = "\n\n# Disclaimer\n\nThis document has been synthetically generated using AI for demonstration purposes. All content, data, recommendations, and analysis are artificially created and should not be used for actual business decisions, implementation, or as factual reference material. Please consult appropriate experts and conduct proper research for real-world applications."
        sections.append(final_note)
        
        # Combine all sections
        full_content = "\n\n".join(sections)
        
        word_count = len(full_content.split())
        print(f" Generated document with {len(sections)-1} sections, approximately {word_count} words")
        return full_content

    def _clean_content(self, content: str) -> str:
        """
        Clean generated content to remove JSON artifacts and code blocks.
        """
        # Remove code blocks first
        content = content.replace('```markdown', '').replace('```json', '').replace('```', '')
        
        # Remove "Here is the document..." prefixes if common
        lines = content.split('\n')
        if len(lines) > 0 and (lines[0].lower().startswith('here is') or lines[0].lower().startswith('sure, here')):
            content = '\n'.join(lines[1:])
            
        content = content.strip()

        # Check for JSON wrapper after stripping code blocks
        if content.startswith('{') and '"content":' in content:
            try:
                import json
                data = json.loads(content)
                if 'content' in data:
                    return data['content']
            except:
                pass
            
        return content
    
    def _strip_markdown(self, text: str) -> str:
        """Remove all Markdown syntax from text."""
        import re
        # Remove bold
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove italic
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove code
        text = re.sub(r'`(.*?)`', r'\1', text)
        return text
    
    def _markdown_to_html(self, text: str) -> str:
        """Convert Markdown formatting to HTML for ReportLab."""
        import re
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Convert *italic* to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Convert `code` to monospace
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        return text

    def create_word_document(self, content: str) -> bytes:
        """
        Create a Word document with the generated content and proper formatting.
        
        This method converts the generated content into a properly formatted
        Word document (.docx) with headings, paragraphs, lists, and other
        formatting elements based on markdown-style indicators in the content.
        
        Args:
            content (str): The generated document content with markdown-style formatting
        
        Returns:
            bytes: The Word document as bytes for file writing
        
        Example:
            >>> content = "# Title\n\nThis is a paragraph with **bold** text."
            >>> doc_bytes = doc_gen.create_word_document(content)
            >>> with open("document.docx", "wb") as f:
            ...     f.write(doc_bytes)
        """
        # Clean content first
        content = self._clean_content(content)
        
        doc = Document()
        
        # Split content into lines for better processing
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
                
            # Check for headings
            if line.startswith('# '):
                heading_text = line.replace('# ', '', 1)
                # Strip any remaining markdown from heading
                heading_text = self._strip_markdown(heading_text)
                doc.add_heading(heading_text, 1)
            elif line.startswith('## '):
                heading_text = line.replace('## ', '', 1)
                heading_text = self._strip_markdown(heading_text)
                doc.add_heading(heading_text, 2)
            elif line.startswith('### '):
                heading_text = line.replace('### ', '', 1)
                heading_text = self._strip_markdown(heading_text)
                doc.add_heading(heading_text, 3)
            # Check for bullet lists
            elif line.startswith('- ') or line.startswith('* '):
                list_text = line[2:].strip()
                p = doc.add_paragraph(style='List Bullet')
                self._add_formatted_text(p, list_text)
            # Check for numbered lists
            elif line and line[0].isdigit() and '. ' in line[:4]:
                list_text = line.split('. ', 1)[1] if '. ' in line else line
                p = doc.add_paragraph(style='List Number')
                self._add_formatted_text(p, list_text)
            else:
                # Regular paragraph
                p = doc.add_paragraph()
                self._add_formatted_text(p, line)
            
            i += 1
        
        doc_bytes = io.BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        return doc_bytes.getvalue()
    
    def _add_formatted_text(self, paragraph, text: str):
        """Add text to paragraph with Markdown formatting converted to Word formatting."""
        import re
        
        # Pattern to match **bold**, *italic*, and plain text
        # This regex splits on markdown markers while keeping them
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
        
        for part in parts:
            if not part:
                continue
            if part.startswith('**') and part.endswith('**'):
                # Bold text
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                # Italic text
                run = paragraph.add_run(part[1:-1])
                run.italic = True
            elif part.startswith('`') and part.endswith('`'):
                # Code/monospace text
                run = paragraph.add_run(part[1:-1])
                run.font.name = 'Courier New'
            else:
                # Plain text
                paragraph.add_run(part)

    def create_pdf_document(self, content: str) -> bytes:
        """
        Create a PDF document with the generated content and professional formatting.
        
        This method converts the generated content into a properly formatted
        PDF document with custom styles, headings, and spacing. Requires
        ReportLab library to be installed.
        
        Args:
            content (str): The generated document content with markdown-style formatting
        
        Returns:
            bytes: The PDF document as bytes for file writing
        
        Raises:
            ImportError: If ReportLab library is not installed
        
        Example:
            >>> content = "# Title\n\nThis is a paragraph with content."
            >>> pdf_bytes = doc_gen.create_pdf_document(content)
            >>> with open("document.pdf", "wb") as f:
            ...     f.write(pdf_bytes)
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab library is not installed. Please install it with: pip install reportlab")
        
        # Clean content first
        content = self._clean_content(content)
        
        pdf_bytes = io.BytesIO()
        doc = SimpleDocTemplate(pdf_bytes, pagesize=letter)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
        )
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
        )
        
        
        story = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 12))
                continue
                
            # Check for headings
            if line.startswith('# '):
                heading_text = line.replace('# ', '', 1)
                # Remove markdown from heading text
                heading_text = self._strip_markdown(heading_text)
                story.append(Paragraph(heading_text, heading_style))
                story.append(Spacer(1, 6))
            elif line.startswith('## '):
                heading_text = line.replace('## ', '', 1)
                heading_text = self._strip_markdown(heading_text)
                story.append(Paragraph(heading_text, subheading_style))
                story.append(Spacer(1, 4))
            else:
                # Regular paragraphs - convert markdown to HTML for ReportLab
                formatted_text = self._markdown_to_html(line)
                story.append(Paragraph(formatted_text, styles['Normal']))
                story.append(Spacer(1, 12))
        
        doc.build(story)
        pdf_bytes.seek(0)
        return pdf_bytes.getvalue()
    
    def _strip_markdown(self, text: str) -> str:
        """Remove all Markdown syntax from text."""
        import re
        # Remove bold
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove italic
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove code
        text = re.sub(r'`(.*?)`', r'\1', text)
        return text
    
    def _markdown_to_html(self, text: str) -> str:
        """Convert Markdown formatting to HTML for ReportLab."""
        import re
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Convert *italic* to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Convert `code` to monospace
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        return text

    def create_text_document(self, content: str) -> bytes:
        """
        Create a plain text document with the generated content.
        
        This method converts the generated content into a clean plain text
        format by removing markdown formatting and adding a simple header.
        
        Args:
            content (str): The generated document content with markdown-style formatting
        
        Returns:
            bytes: The text document as bytes for file writing
        
        Example:
            >>> content = "# Title\n\nThis is a paragraph with content."
            >>> text_bytes = doc_gen.create_text_document(content)
            >>> with open("document.txt", "wb") as f:
            ...     f.write(text_bytes)
        """
        # Clean content first
        content = self._clean_content(content)
        
        # Clean up the content for plain text
        text_content = content.replace('# ', '')
        text_content = text_content.replace('## ', '')
        
        # Add a simple header
        header = "="*80 + "\n"
        header += "SYNTHETIC DOCUMENT - GENERATED CONTENT\n" 
        header += "="*80 + "\n\n"
        
        final_content = header + text_content
        return final_content.encode('utf-8')

    def generate_document(
        self, 
        content_type: str, 
        pages: int, 
        subject: str, 
        file_format: str
    ) -> Tuple[str, str]:
        """
        Main document generation orchestrator.
        
        This method coordinates the entire document generation process, choosing
        between single-call and iterative approaches based on document length,
        then formatting the content into the requested output format.
        
        Args:
            content_type (str): Type of document to generate. Must be one of:
                - "whitepaper": Technical analysis and methodology
                - "article": In-depth analysis with case studies
                - "report": Business analysis with strategic recommendations
                - "proposal": Project proposals with timelines and budgets
                - "design": IT system design and architecture documents
            pages (int): Target number of pages for the document
            subject (str): Subject/topic for the document content
            file_format (str): Output format. Must be one of:
                - "Word Document (.docx)"
                - "PDF Document (.pdf)"
                - "Text File (.txt)"
        
        Returns:
            Tuple[str, str]: (file_path, status_message)
                - file_path: Path to the generated document file
                - status_message: Success message with generation details
        
        Example:
            >>> doc_gen = DocumentGenerator(data_gen)
            >>> path, status = doc_gen.generate_document(
            ...     "article", 5, "AI Governance", "Word Document (.docx)"
            ... )
            >>> print(f"Generated: {path}")
            >>> print(status)
        """
        # Use iterative approach for longer documents (3+ pages)
        if pages >= 3:
            content = self.generate_document_content_iterative(content_type, pages, subject)
            print(f" Used iterative approach for {pages} pages")
        else:
            content = self.generate_document_content(content_type, pages, subject)
            print(f" Used standard approach for {pages} pages")
        
        if file_format == "Word Document (.docx)":
            file_bytes = self.create_word_document(content)
            suffix = '.docx'
        elif file_format == "PDF Document (.pdf)":
            file_bytes = self.create_pdf_document(content)
            suffix = '.pdf'
        else:  # Text File (.txt)
            file_bytes = self.create_text_document(content)
            suffix = '.txt'
        
        # Save to temporary file and return path
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix='synthetic_') as tmp_file:
            tmp_file.write(file_bytes)
            temp_path = tmp_file.name
        
        return temp_path, f" Generated {pages}-page {content_type} about '{subject}' successfully!"
