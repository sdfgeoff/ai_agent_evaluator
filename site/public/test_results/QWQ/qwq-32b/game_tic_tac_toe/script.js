let board = ['', '', '', '', '', '', '', '', ''];
let currentPlayer = 'X';
let gameOver = false;

function initBoard() {
    const boardElement = document.getElementById('board');
    boardElement.innerHTML = '';
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.id = 'cell' + i;
        cell.addEventListener('click', () => cellClicked(i));
        boardElement.appendChild(cell);
    }
}

function cellClicked(index) {
    if (gameOver || board[index] !== '') return;
    board[index] = currentPlayer;
    const cell = document.getElementById('cell' + index);
    cell.innerHTML = currentPlayer;
    cell.classList.add(currentPlayer);
    if (checkWin()) {
        alert(currentPlayer + ' wins!');
        gameOver = true;
    } else if (checkDraw()) {
        alert('Draw!');
        gameOver = true;
    } else {
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    }
}

function checkWin() {
    const wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
        [0, 4, 8], [2, 4, 6] // Diagonals
    ];
    for (let i = 0; i < wins.length; i++) {
        const [a, b, c] = wins[i];
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            return true;
        }
    }
    return false;
}

function checkDraw() {
    return board.every(cell => cell !== '');
}

function resetGame() {
    board = ['', '', '', '', '', '', '', '', ''];
    currentPlayer = 'X';
    gameOver = false;
    initBoard();
}

window.onload = initBoard;