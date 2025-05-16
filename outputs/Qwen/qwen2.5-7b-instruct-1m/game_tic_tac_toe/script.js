const cells = document.querySelectorAll('.cell');

let board = [
    [null, null, null],
    [null, null, null],
    [null, null, null]
];

let currentPlayer = 'X';

function updateBoard(selectedCell) {
    let cellIndex = parseInt(selectedCell.getAttribute('data-index')) - 1;
    board[cellIndex[0]][cellIndex[1]] = currentPlayer;
}

function checkWin() {
    const lines = [
        [[0, 0], [0, 1], [0, 2]],
        [[1, 0], [1, 1], [1, 2]],
        [[2, 0], [2, 1], [2, 2]],

        [[0, 0], [1, 0], [2, 0]],
        [[0, 1], [1, 1], [2, 1]],
        [[0, 2], [1, 2], [2, 2]],

        [[0, 0], [1, 1], [2, 2]],
        [[0, 2], [1, 1], [2, 0]]
    ];

    for (let line of lines) {
        const [a, b, c] = line;
        if (board[a[0]][a[1]] && board[a[0]][a[1]] === board[b[0]][b[1]] && board[a[0]][a[1]] === board[c[0]][c[1]]) {
            alert(currentPlayer + ' wins!');
            return true;
        }
    }

    return false;
}

function switchPlayer() {
    currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
}

function handleButtonClick(event) {
    let targetCell = event.target;
    if (!targetCell.classList.contains('button')) {
        return;
    }
    updateBoard(targetCell);
    checkWin();
    targetCell.disabled = true;
    switchPlayer();
}

function init() {
    cells.forEach((cell, index) => {
        cell.setAttribute('data-index', (index + 1));
        cell.addEventListener('click', handleButtonClick);
    });
}
init();