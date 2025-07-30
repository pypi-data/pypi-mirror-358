from web2json.ai_extractor import *
from web2json.postprocessor import *
from web2json.preprocessor import *
from pydantic import BaseModel
import sys

class Pipeline:
    """Run preprocessing, extraction and post-processing steps."""

    def __init__(
        self,
        preprocessor: Preprocessor,
        ai_extractor: AIExtractor,
        postprocessor: PostProcessor,
        *,
        debug: bool = False,
    ) -> None:
        """Create a pipeline from the supplied processing components.

        Args:
            preprocessor: Component used to clean and normalise the input.
            ai_extractor: Object responsible for calling the language model.
            postprocessor: Component used to repair and enrich the model output.
            debug: If ``True`` print intermediate results to ``stderr``.
        """
        self.preprocessor = preprocessor
        self.ai_extractor = ai_extractor
        self.postprocessor = postprocessor
        self.debug = debug

    def run(self, content: str, is_url: bool, schema:BaseModel) -> dict:
        """
        Run the entire pipeline: preprocess, extract, and postprocess.

        Args:
            content (str): The raw content to process.
            is_url (bool): Whether the content is a URL or raw text.
            schema (BaseModel): The schema defining the structure of the expected output.

        Returns:
            dict: The final structured data after processing. The cleaned
            content is also provided to the post-processor so that missing URL
            fields may be recovered when link patterns are configured.
        """
        # Step 1: Preprocess the content
        preprocessed_content = self.preprocessor.preprocess(content, is_url)
        if self.debug:
            print("Preprocessed content:", file=sys.stderr)
            print(preprocessed_content, file=sys.stderr)
            print("+" * 80, file=sys.stderr)
        # Step 2: Extract structured information using AI
        extracted_data = self.ai_extractor.extract(preprocessed_content, schema)
        if self.debug:
            print("Extracted data:", extracted_data, file=sys.stderr)
            print("+" * 80, file=sys.stderr)
        # Step 3: Post-process the extracted data
        html = getattr(self.preprocessor, "last_html", None)
        final_output = self.postprocessor.process(
            extracted_data,
            preprocessed_content,
            html,
        )
        if self.debug:
            print(f"Final output: {final_output}", file=sys.stderr)
            print("+" * 80, file=sys.stderr)
        
        return final_output
