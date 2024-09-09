from typing import Callable, Dict


class Key:
    def __init__(self, action: Callable, continuous: bool = True) -> None:
        self.pressed: bool = False
        self.switched: bool = False
        self.action: Callable = action
        self.continuous: bool = continuous

    def handle(self) -> None:
        if self.pressed and self.continuous:
            print("press action")
            self.action()
        elif self.switched and not self.continuous:
            print("release action")
            self.action()
        self.switched = False

    def press(self) -> None:
        print("press")
        self.pressed = True

    def release(self) -> None:
        print("release")
        self.pressed = False
        self.switched = True


class InputHandler:
    def __init__(self) -> None:
        self.keys: Dict[int, Key] = dict()

    def add_key(self, key_id: int, action: Callable, continuous: bool = True) -> None:
        self.keys[key_id] = Key(action, continuous)

    def update_key(
        self, key_id: int, pressed: bool = False, released: bool = False
    ) -> None:
        if key_id in self.keys:
            if pressed:
                self.keys[key_id].press()
            elif released:
                self.keys[key_id].release()

    def handle_keys(self) -> None:
        for key_id in self.keys:
            self.keys[key_id].handle()
