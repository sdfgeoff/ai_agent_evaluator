let currentPlayer = 'X';
const boardElements = document.querySelectorAll('.cell');
const gameBoard = document.getElementById('game-board');

function createBoard() {
    let boardArray = [];
    for (let row = 0; row < 3; row++) {
        const rowArray = [];
        for (let col = 0; col < 3; col++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.addEventListener('click', handleCellClick);
            rowArray.push(cell);
        }
        boardArray.push(rowArray);
    }
    gameBoard.innerHTML = '';
    gameBoard.appendChild(document.createElement('table'));
    const table = document.querySelector('#game-board table');

    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            table.rows[i].cells[j].appendChild(boardArray[i][j]);
        }
    }
}

function handleCellClick(event) {
    const clickedCell = event.target;
    if (!clickedCell.innerText && currentPlayer === 'X') {
        clickedCell.innerText = currentPlayer;
        currentPlayer = 'O';
    } else if (!clickedCell.innerText && currentPlayer === 'O') {
        clickedCell.innerText = currentPlayer;
        currentPlayer = 'X';
    }
}