"""
AI-powered comment generator using Gemini 2.0 Flash model from Google.
"""

from typing import Dict, Optional, Any

from google import genai
from google.genai import types


class GeminiCommentGenerator:
    """Generate code comments using Gemini 2.0 Flash model."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini comment generator.

        Args:
            api_key: Google AI API key.
        """
        try:
            self.genai = genai
            self.api_key = api_key

            if not self.api_key:
                raise ValueError("No API key provided. Please set the GOOGLE_API_KEY environment variable in your .env file")

            self.client = genai.Client(api_key=self.api_key)
            print("Successfully initialized Gemini comment generator")

        except ImportError:
            raise ImportError("Failed to import Google AI SDK. Please install it with: pip install google-genai")

    def generate_comment(self, code_snippet: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a comment for a code snippet using Gemini 2.0 Flash.

        Args:
            code_snippet: The code to generate a comment for
            context: Additional context about the code (file path, function name, etc.)

        Returns:
            Generated comment as a string
        """
        # Create prompt with context
        prompt = self._create_prompt(code_snippet, context)

        try:
            # Generate content with Gemini
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40,
                )
            )

            # Extract and clean up the comment text
            return self._clean_comment(response.text)

        except Exception as e:
            print(f"Error generating comment with Gemini: {str(e)}")
            return f"Error generating comment: {str(e)}"

    def _create_prompt(self, code_snippet: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Create a prompt for Gemini based on the code and context."""
        context_info = ""
        if context:
            if context.get("file_path"):
                context_info += f"File: {context['file_path']}\n"
            if context.get("class_name"):
                context_info += f"Class: {context['class_name']}\n"
            if context.get("function_name"):
                context_info += f"Function: {context['function_name']}\n"

        prompt = f"""You are an expert programmer who writes clear and helpful code comments.
        
{context_info}
Please write a detailed comment for the following code:

{code_snippet}
        
Generate ONLY the comment text without any additional explanation or markdown. The comment should explain what the code does, important parameters, return values, and any important logic or edge cases."""

        return prompt

    def _clean_comment(self, text: str) -> str:
        """Clean up the generated comment."""
        # Remove any triple backticks and language indicators
        text = text.replace("```", "").strip()

        # Remove any common prefixes the model might add
        prefixes = ["Comment:", "Here's a comment:", "/*", "*/", "//", "#"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()

        return text
