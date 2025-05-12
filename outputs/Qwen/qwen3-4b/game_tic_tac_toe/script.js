let currentPlayer = 'X';
const cells = document.querySelectorAll('#board .cell');
const message = document.getElementById('message');
const board = Array.from(cells);
let gameActive = true;

function resetGame() {
    currentPlayer = 'X';
    gameActive = true;
    message.textContent = `Player ${currentPlayer}'s turn`;
    board.forEach(cell => cell.textContent = '');
}

function checkWin(player) {
    const lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ];
    return lines.some(line => {
        return line.every(index => board[index].textContent === player);
    });
}

function checkTie() {
    return !board.includes(null) && !checkWin('X') && !checkWin('O');
}

cells.forEach(cell => {
    cell.addEventListener('click', () => {
        if (!gameActive) return;
        if (cell.textContent !== '') return;

        cell.textContent = currentPlayer;
        if (checkWin(currentPlayer)) {
            message.textContent = `Player ${currentPlayer} wins!`;
            gameActive = false;
            return;
        }
        if (checkTie()) {
            message.textContent = 'It`s a tie!';
            gameActive = false;
            return;
        }
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        message.textContent = `Player ${currentPlayer}'s turn`;
    });
});

// Initialize game
resetGame();