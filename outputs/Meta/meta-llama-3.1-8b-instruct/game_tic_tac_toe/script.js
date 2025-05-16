/* global document, console */

const cells = document.querySelectorAll('.cell');
const gameBoard = document.querySelector('.game-board');
let currentPlayer = 'X';
let gameOver = false;

cells.forEach(cell => {
  cell.addEventListener('click', handleCellClick);
});

function handleCellClick(event) {
  if (gameOver) return;
  const cell = event.target;
  if (cell.textContent !== '') return;
  cell.textContent = currentPlayer;
  checkForWin();
  currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
}

function checkForWin() {
  const winningCombinations = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
  for (const combination of winningCombinations) {
    if (
      cells[combination[0]].textContent === cells[combination[1]].textContent &&
      cells[combination[1]].textContent === cells[combination[2]].textContent &&
      cells[combination[0]].textContent !== ''
    ) {
      gameBoard.style.display = 'none';
      alert(`Player ${cells[combination[0]].textContent} wins!`);
      gameOver = true;
    }
  }
}

function task_complete() {
  // No implementation required for this task.
}