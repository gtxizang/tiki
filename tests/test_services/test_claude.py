from tiki.services.claude import ClaudeService


class TestClaudeServiceParsing:
    def setup_method(self):
        self.service = ClaudeService.__new__(ClaudeService)

    def test_parse_valid_json(self):
        result = self.service._parse_response(
            '{"themes": [], "description": "A doc.", "keywords": ["test"]}'
        )
        assert result["description"] == "A doc."
        assert result["keywords"] == ["test"]

    def test_parse_with_markdown_fences(self):
        result = self.service._parse_response(
            '```json\n{"themes": [], "description": "A doc.", "keywords": []}\n```'
        )
        assert result["description"] == "A doc."

    def test_parse_invalid_json(self):
        result = self.service._parse_response("this is not json")
        assert result == {}

    def test_build_prompt_minimal(self):
        prompt = self.service._build_prompt("Some text", "", "", "", "")
        assert "Some text" in prompt

    def test_build_prompt_full(self):
        prompt = self.service._build_prompt(
            "Content", "My Title", "Author Name", "application/pdf", "en"
        )
        assert "My Title" in prompt
        assert "Author Name" in prompt
        assert "application/pdf" in prompt
        assert "en" in prompt
