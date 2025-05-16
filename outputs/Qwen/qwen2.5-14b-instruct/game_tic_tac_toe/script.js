document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('game-board');
    
    // Initialize board as an array of empty strings for each cell
    let currentBoard = Array(9).fill('');
    let currentPlayer = 'X';
    
    function createBoard() {
        currentBoard.forEach((cell, index) => {
            const divCell = document.createElement('div');
            divCell.classList.add('cell');
            divCell.textContent = '';
            divCell.addEventListener('click', () => makeMove(index));
            board.appendChild(divCell);
        });
    }

    function makeMove(cellIndex) {
        if (currentBoard[cellIndex] === '') {
            currentBoard[cellIndex] = currentPlayer;
            
            const cellElements = document.querySelectorAll('.cell');
            cellElements[cellIndex].textContent = currentPlayer;

            if (checkWin(currentPlayer)) {
                alert(`Congratulations ${currentPlayer}, you won!`);
                resetGame();
            } else if (!currentBoard.includes('')) {
                alert("It's a draw!");
                resetGame();
            } else {
                switchPlayer();
            }
        }
    }

    function checkWin(player) {
        const winConditions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ];

        return winConditions.some(condition => {
            const [a, b, c] = condition;
            return currentBoard[a] === player && currentBoard[b] === player && currentBoard[c] === player;
        });
    }

    function switchPlayer() {
        currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
    }

    function resetGame() {
        location.reload();
    }

    createBoard();
});