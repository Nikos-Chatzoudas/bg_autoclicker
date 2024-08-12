import pyautogui
import keyboard

def main():
    pyautogui.FAILSAFE = False
    last_position = None

    try:
        while True:
            x, y = pyautogui.position()
            if (x, y) != last_position:
                print(f"Mouse position: X={x}, Y={y}")
                last_position = (x, y)
            if keyboard.is_pressed('q'):
                print("Script stopped by the user.")
                print(f"Last known mouse position: X={last_position[0]}, Y={last_position[1]}")
                print(f"{last_position[0]},{last_position[1]}")
                break
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    input()