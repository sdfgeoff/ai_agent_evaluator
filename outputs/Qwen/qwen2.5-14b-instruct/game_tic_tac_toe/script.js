// script.js

let currentPlayer = 'X';
const boardSize = 3;

function initBoard() {
    const boardContainer = document.getElementById('game-board');
    for (let i = 0; i < boardSize * boardSize; ++i) {
        let cellElement = createCell(i);
        boardContainer.appendChild(cellElement);
    }
}

function createCell(index) {
    // Create a cell
    let cellElement = document.createElement('div');
    cellElement.classList.add('cell');
    cellElement.addEventListener('click', placeMark);

    return cellElement;
}

function placeMark(event) {
    const clickedCell = event.target;
    if (clickedCell.textContent === '') {
        clickedCell.textContent = currentPlayer;
        checkWinner();
    }
}

function checkWinner() {
    // Simple checks for a win condition
    let cells = document.querySelectorAll('.cell');
    let boardState = Array.from(cells).map(cell => cell.textContent);

    // Check horizontal, vertical, and diagonal lines.
    const winningCombinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],

        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],

        [0, 4, 8],
        [2, 4, 6]
    ];

    for (let combo of winningCombinations) {
        let [a, b, c] = combo;
        if (boardState[a] && boardState[a] === boardState[b] && boardState[a] === boardState[c]) {
            alert(`Player ${boardState[a]} wins!`);
            return resetGame();
        }
    }

    // Check for a draw
    let isDraw = true;

    cells.forEach(cell => {
        if (cell.textContent === '') isDraw = false;
    });

    if(isDraw) { 
        alert('It\'s a draw!');
        resetGame();
    }

    // Switch turns
    currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
}

function resetGame() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => cell.textContent = '');
}