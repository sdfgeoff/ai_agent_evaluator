const board = document.getElementById('board');
const resetButton = document.getElementById('reset');
let currentPlayer = 'X';
let cells = [];
let gameActive = true;

// Create board cells
for (let i = 0; i < 9; i++) {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    cell.dataset.index = i;
    cell.addEventListener('click', handleCellClick);
    board.appendChild(cell);
    cells.push(cell);
}

// Handle cell click
function handleCellClick(e) {
    const index = e.target.dataset.index;
    if (gameActive && !e.target.textContent) {
        e.target.textContent = currentPlayer;
        checkWin();
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    }
}

// Check for win
function checkWin() {
    const winConditions = [
        [0,1,2], [3,4,5], [6,7,8], // rows
        [0,3,6], [1,4,7], [2,5,8], // columns
        [0,4,8], [2,4,6] // diagonals
    ];

    for (const condition of winConditions) {
        const [a, b, c] = condition;
        if (cells[a].textContent && cells[a].textContent === cells[b].textContent && cells[a].textContent === cells[c].textContent) {
            gameActive = false;
            alert(`Player ${cells[a].textContent} wins!`);
            return;
        }
    }

    // Check for draw
    if (cells.every(cell => cell.textContent)) {
        alert('Draw!');
        gameActive = false;
    }
}

// Reset game
resetButton.addEventListener('click', () => {
    cells.forEach(cell => cell.textContent = '');
    currentPlayer = 'X';
    gameActive = true;
});