from llobot.prompts import asking_prompt_section, PromptSection

def test_asking_prompt_section():
    section = asking_prompt_section()
    assert isinstance(section, PromptSection)
    content = str(section)
    assert "How to ask questions" in content
    assert "Stop and ask for the user's feedback" in content
