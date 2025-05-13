let boardState = Array(9).fill('');
let currentPlayer = 'X';
let gameOver = false;

function createBoard() {
    const board = document.getElementById('board');
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.index = i;
        cell.addEventListener('click', handleCellClick);
        board.appendChild(cell);
    }
}

function handleCellClick(event) {
    const cell = event.target;
    const index = cell.dataset.index;
    if (boardState[index] === '' && !gameOver) {
        cell.textContent = currentPlayer;
        boardState[index] = currentPlayer;
        if (checkWin()) {
            document.getElementById('message').textContent = `Player ${currentPlayer} wins!`;
            gameOver = true;
        } else if (boardState.every(cell => cell !== '')) {
            document.getElementById('message').textContent = "It's a draw!";
            gameOver = true;
        } else {
            currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        }
    }
}

function checkWin() {
    const winningCombos = [
        [0,1,2], [3,4,5], [6,7,8], // rows
        [0,3,6], [1,4,7], [2,5,8], // columns
        [0,4,8], [2,4,6] // diagonals
    ];

    return winningCombos.some(combo => {
        return combo.every(index => boardState[index] === currentPlayer);
    });
}

function resetGame() {
    boardState = Array(9).fill('');
    currentPlayer = 'X';
    gameOver = false;
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.textContent = '';
    });
    document.getElementById('message').textContent = '';
    const board = document.getElementById('board');
    board.innerHTML = '';
    createBoard();
}

document.addEventListener('DOMContentLoaded', function() {
    createBoard();
});