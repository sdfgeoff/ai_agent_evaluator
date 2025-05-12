// Initialize the game board
let board = [
    ['', '', ''],
    ['', '', ''],
    ['', '', '']
];

// Player marker (X or O)
let currentPlayer = 'X';

// Function to make a move on the board
function makeMove(row, col) {
    if (!board[row][col]) {
        board[row][col] = currentPlayer;
        document.getElementById(`cell-${row}-${col}`).innerText = currentPlayer;
        checkWinner();
        switchPlayerTurn();
    }
}

// Switch player turn between X and O
function switchPlayerTurn() {
    currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
}

// Check for a winner or draw
function checkWinner() {
    // Check rows, columns, diagonals for a win condition
    let possibleLines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ];

    for (let line of possibleLines) {
        let a = board[Math.floor(line[0] / 3)][line[0] % 3];
        let b = board[Math.floor(line[1] / 3)][line[1] % 3];
        let c = board[Math.floor(line[2] / 3)][line[2] % 3];

        if (a === '' || b === '' || c === '') continue;

        if (a === b && b === c) {
            alert(`Player ${a} wins!`);
            restartGame();
            return;
        }
    }
}

// Restarts the game by resetting the board and player turn.
function restartGame() {
    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[i].length; j++) {
            document.getElementById(`cell-${i}-${j}`).innerText = '';
            board[i][j] = '';
        }
    }
}

// Add event listeners to game cells
window.onload = function () {
    let boardContainer = document.getElementById('game-board');
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            let cell = document.createElement('div');
            cell.id = `cell-${i}-${j}`;
            cell.classList.add('game-cell');
            boardContainer.appendChild(cell);
            cell.addEventListener('click', () => makeMove(i, j));
        }
    }
}