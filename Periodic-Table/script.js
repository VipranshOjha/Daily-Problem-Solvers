console.log('Hello from script.js!');

// Constants for configuration
const totalRows = 10;
const totalColumns = 18;
const tableId = 'periodic-table';
const csvFilePath = 'data.csv';

// select the dom
const table = document.getElementById(tableId);

// create the elements
// Set to 10 rows to account for additional spacing
// and the inclusion of the "La-Lu" and "Ac-Lr" series.
for (let i = 0; i < totalRows; i++) {
    const row = document.createElement('tr');
    for (let j = 0; j < totalColumns; j++) {
        const cell = document.createElement('td');
        row.appendChild(cell);
    }
    table.appendChild(row);
}


function showDetails(rowElements) {
    const mainDiv = document.getElementById('main-div');
    const detailDiv = document.getElementById('detailDiv');
    if (mainDiv.style.zIndex === '9999') {
        mainDiv.style.zIndex = '-9999';
        // set visibility to none
        detailDiv.innerHTML = '';
    } else {
        mainDiv.style.zIndex = '9999';
        // innterHTML
        const atomicNumber = rowElements[1];
        const symbol = rowElements[2];
        const name = rowElements[3];

        detailDiv.innerHTML =
            `Atomic Number: ${atomicNumber}<br>` +
            `Symbol: ${symbol}<br>Name: ${name}`;
    };


}

const handleCSVData = (data) => {
    const cells = table.getElementsByTagName('td');
    data.split('\n').forEach((row, index) => {

        const rowElements = row.split(';');

        const x = parseInt(rowElements[4].trim());
        const y = parseInt(rowElements[5].trim());

        // ignore the first row
        if (!isNaN(x) && !isNaN(y) && index !== 0) {

            // for each cell...
            const cellIndex = (x - 1) + (y - 1) * totalColumns;
            const cell = cells[cellIndex];
            if (cell !== undefined) {
                const symbol = rowElements[2].trim();
                cell.innerHTML = symbol.trim();
                let elementClass = rowElements[6].trim().toLowerCase();

                // Normalize lanthanides/actinides spelling
                if (elementClass === 'lantanides') elementClass = 'lanthanides';
                if (elementClass === 'actinides') elementClass = 'actinides';

                cell.classList.add(elementClass);

                // add event listener
                // cell.onclick = showDetails;
                cell.addEventListener('click', function () {
                    showDetails(rowElements);
                }, false);
            }
        }
    })
}


// readCSVFile
fetch(csvFilePath)
    .then(response => response.text())
    .then(handleCSVData)
    .catch(error => console.error('Error loading the CSV file:', error));

