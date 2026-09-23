from core.brain import LenoBrain
from core.voice import LenoVoice
from core.vision import LenoVision


def main():
    print("=" * 55)
    print("                    LENO")
    print("          Local AI Personal Assistant")
    print("=" * 55)

    brain = LenoBrain()
    voice = LenoVoice()
    vision = LenoVision()

    print("\n👁️ Vision: READY")
    print("🎤 Voice: READY")
    print("🧠 Brain: READY")

    voice.speak("Hey Boss. LENO is ready.")

    last_person = None

    while True:
        try:
            is_boss = False
            person_name = None
            expression = "neutral"

            person = vision.get_current_person()

            if person:
                expression = person.get(
                    "expression",
                    "neutral"
                )

                if person.get("is_boss", False):
                    is_boss = True
                    person_name = "Boss"

                    print(
                        f"👑 Boss detected | "
                        f"Expression: {expression} | "
                        f"Confidence: "
                        f"{person.get('confidence', 0):.2f}"
                    )

                else:
                    is_boss = False
                    person_name = brain.get_guest_name()

                    if person_name:
                        print(
                            f"👤 {person_name} | "
                            f"Expression: {expression}"
                        )
                    else:
                        print(
                            f"👤 Unknown guest | "
                            f"Expression: {expression}"
                        )

                last_person = {
                    "is_boss": is_boss,
                    "name": person_name,
                    "expression": expression
                }

            elif last_person:
                is_boss = last_person["is_boss"]
                person_name = last_person["name"]
                expression = last_person["expression"]

            user_message = voice.listen()

            if not user_message:
                continue

            command = user_message.lower().strip()

            if command in {
                "exit",
                "quit",
                "goodbye",
                "shut down",
                "stop"
            }:
                if is_boss:
                    voice.speak(
                        "Alright Boss. I'll be here when you need me."
                    )
                else:
                    voice.speak(
                        "It was nice talking with you. See you later."
                    )

                break

            vision_context = (
                f"The person's estimated facial expression is "
                f"{expression}. Treat this only as a visual cue "
                f"and not certainty about their actual emotion."
            )

            answer = brain.think(
                user_message=user_message,
                person_name=person_name,
                is_boss=is_boss,
                vision_context=vision_context
            )

            voice.speak(answer)

        except KeyboardInterrupt:
            print("\n🛑 LENO stopped.")
            break

        except Exception as error:
            print(f"\n❌ LENO error: {error}")

            try:
                voice.speak(
                    "I ran into a problem there. "
                    "Give me another try."
                )
            except Exception:
                pass

    vision.close()


if __name__ == "__main__":
    main()