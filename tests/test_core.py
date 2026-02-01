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


def test_infers_tool_with_accents_and_punctuation():
    assistant = AdaptiveAssistant()
    response = assistant.interact("Peux-tu faire un résumé, s'il te plaît ?")
    assert "resume" in assistant.state.tools
    assert "Outil 'resume'" in response
