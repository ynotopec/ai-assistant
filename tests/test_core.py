from ai_assistant.core import AdaptiveAssistant


def test_interaction_updates_state():
    assistant = AdaptiveAssistant()
    response = assistant.interact("bonjour")
    assert "bien commun" in response
    assert assistant.state.knowledge


def test_tool_creation():
    assistant = AdaptiveAssistant()
    response = assistant.interact("outil:analyse")
    assert "analyse" in assistant.state.tools
    assert "Outil 'analyse'" in response
