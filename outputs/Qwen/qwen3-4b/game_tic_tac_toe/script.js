let currentPlayer = 'X';
const board = document.getElementById('board');
const status = document.getElementById('status');

// Create the board
for (let i = 0; i < 9; i++) {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    cell.addEventListener('click', () => handleCellClick(i));
    board.appendChild(cell);
}

function handleCellClick(index) {
    // Check if the cell is already filled
    if (board.children[index].textContent !== '') return;

    board.children[index].textContent = currentPlayer;
    checkWin();
    currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    updateStatus();
}

function checkWin() {
    const winConditions = [
        [0,1,2], [3,4,5], [6,7,8], // rows
        [0,3,6], [1,4,7], [2,5,8], // columns
        [0,4,8], [2,4,6]          // diagonals
    ];

    for (let condition of winConditions) {
        const [a, b, c] = condition;
        if (board.children[a].textContent === board.children[b].textContent && 
            board.children[b].textContent === board.children[c].textContent && 
            board.children[a].textContent !== '') {
            status.textContent = `Player ${board.children[a].textContent} wins!`;
            return;
        }
    }

    // Check for draw
    if (['X', 'O'].every(player => [...board.children].some(cell => cell.textContent === player))) {
        status.textContent = "It's a draw!";
    }
}

function updateStatus() {
    status.textContent = `Player ${currentPlayer}'s turn`;
}

// Reset button
const resetButton = document.createElement('button');
resetButton.textContent = 'Reset';
resetButton.style.display = 'block';
resetButton.style.marginLeft = 'auto';
resetButton.style.marginRight = 'auto';
resetButton.style.marginTop = '10px';
resetButton.addEventListener('click', () => {
    for (let i = 0; i < 9; i++) {
        board.children[i].textContent = '';
    }
    currentPlayer = 'X';
    status.textContent = `Player ${currentPlayer}'s turn`;
});
document.body.appendChild(resetButton);