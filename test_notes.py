from agent.notes_engine import NotesEngine

eng = NotesEngine()

print("A. TEST note_previous:")
print(eng.note_previous("The generator uses retrieved info to produce context-aware text"))
print()

print("B. TEST note_current:")
print(eng.note_current(
    question="what is rag?",
    answer="retrieval augmented generation"
))
print()

print("C. TEST list:")
print(eng.list_notes())
