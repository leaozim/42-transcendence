
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 640;
const OFFSET = 10;
const CENTER_OF_SCREEN = new Vector2(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
// Same as srcs_game/physics.py: paddles start vertically centred.
const LEFT_PADDLE_START_POSITION = new Vector2(0 + OFFSET, CANVAS_HEIGHT / 2);
const RIGHT_PADDLE_START_POSITION = new Vector2(CANVAS_WIDTH - OFFSET, CANVAS_HEIGHT / 2);

PLAYER_LEFT = 0
PLAYER_RIGHT = 1