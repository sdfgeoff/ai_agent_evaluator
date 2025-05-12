const gameContainer = document.getElementById('game');
const statusText = document.getElementById('status');
const resetButton = document.getElementById('reset');

let board = Array(9).fill(null);
let currentPlayer = 'X';
let gameActive = true;

function createBoard() {
    gameContainer.innerHTML = '';
    board = Array(9).fill(null);
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.classList.add('cell');
        cell.dataset.index = i;
        cell.addEventListener('click', handleCellClick);
        gameContainer.appendChild(cell);
    }
}

function handleCellClick(e) {
    const index = e.target.dataset.index;
    if (!gameActive || board[index]) return;

    board[index] = currentPlayer;
    e.target.textContent = currentPlayer;

    if (checkWin()) {
        statusText.textContent = `Player ${currentPlayer} wins!`;
        gameActive = false;
    } else if (board.every(cell => cell)) {
        statusText.textContent = 'It’s a draw!';
        gameActive = false;
    } else {
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        statusText.textContent = `Player ${currentPlayer}'s turn`;
    }
}

function checkWin() {
    const winPatterns = [
        [0,1,2], [3,4,5], [6,7,8], // rows
        [0,3,6], [1,4,7], [2,5,8], // columns
        [0,4,8], [2,4,6]           // diagonals
    ];

    return winPatterns.some(pattern => {
        const [a,b,c] = pattern;
        return board[a] && board[a] === board[b] && board[a] === board[c];
    });
}

resetButton.addEventListener('click', () => {
    currentPlayer = 'X';
    gameActive = true;
    statusText.textContent = `Player ${currentPlayer}'s turn`;
    createBoard();
});

// Initialize the game
createBoard();