const cells = document.querySelectorAll('.cell');
const restartButton = document.getElementById('restartButton');

let isXTurn = true;

// All possible winning combinations
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

// Handle a cell click event
function handleClick(event) {
  const cell = event.target;
  const currentPlayer = isXTurn ? 'X' : 'O';

  // if cell is already taken, ignore click
  if (cell.textContent !== '') {
    return;
  }

  // Place the player's mark
  cell.textContent = currentPlayer;

  // Check for win
  if (checkWin(currentPlayer)) {
    setTimeout(() => {
      alert(`${currentPlayer} wins!`);
      restartGame();
    }, 100);
    return;
  }

  // Check for draw
  if (checkDraw()) {
    setTimeout(() => {
      alert('Draw!');
      restartGame();
    }, 100);
    return;
  }

  // Swap turns
  isXTurn = !isXTurn;
}

// Check if the current player has any winning combination
function checkWin(player) {
  return winningCombinations.some(combination => {
    return combination.every(index => {
      return cells[index].textContent === player;
    });
  });
}

// Check if all cells are filled and no empty cell left
function checkDraw() {
  return Array.from(cells).every(cell => cell.textContent !== '');
}

// Reset the game board
function restartGame() {
  cells.forEach(cell => cell.textContent = '');
  isXTurn = true;
}

// Attach click event listeners to each cell
cells.forEach(cell => cell.addEventListener('click', handleClick));

// Attach click event listener to the restart button
restartButton.addEventListener('click', restartGame);
