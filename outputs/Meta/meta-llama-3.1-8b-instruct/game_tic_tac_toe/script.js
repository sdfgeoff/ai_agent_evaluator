const gameBoard = document.getElementById('game-board'); let playerTurn = 'X'; let gameover = false;

function handleCellClick(event) {
  if (gameover) return;
  const cell = event.target;
  if (cell.textContent === '') {
    cell.textContent = playerTurn;
    checkForWin();
    if (!gameover) {
      playerTurn = playerTurn === 'X' ? 'O' : 'X';
    }
  }
}

function checkForWin() {
  const cells = gameBoard.querySelectorAll('.cell');
  for (const cell of cells) {
    if (cell.textContent === '' || cell.textContent === playerTurn) continue;
    if (cell.textContent !== '') {
      gameover = true;
      alert(`${playerTurn} wins!`);
      return;
    }
  }
}

gameBoard.addEventListener('click', handleCellClick);