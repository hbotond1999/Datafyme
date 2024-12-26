class ChartHelper {
    constructor(url, parentContainer) {
        this.parent = parentContainer;
        this.url = url;
        this.getChartData();
    }

    renderChart(data) {
        if (data.type === "TABLE") {
            this.renderTable(data.chart_data);
        } else {
            this.renderCanvasChart(data);
        }
    }

    renderCanvasChart(charData) {
        const div = document.createElement("div");
        div.classList.add("chart-container");
        const canvas = document.createElement('canvas');
        canvas.height = 200;
        canvas.width = 200;
        div.append(canvas);
        this.parent.append(div);
        const ctx = canvas.getContext('2d');
        new Chart(ctx, charData.chart_data);
    }

    renderTable(tableData) {
        const table = document.createElement('table');
        table.classList.add('table', 'table-striped'); // Bootstrap classes

        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        const headers = Object.keys(tableData);

        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText.replace('_', ' '); // Replace underscores with spaces for display
            headerRow.appendChild(th);
        });

        const tbody = table.createTBody();

        // Assuming all arrays in tableData have the same length
        const numRows = tableData[headers[0]].length;

        for (let i = 0; i < numRows; i++) {
            const row = tbody.insertRow();
            headers.forEach(header => {
                const cell = row.insertCell();
                cell.textContent = tableData[header][i];
            });
        }

        this.parent.appendChild(table);
    }



    getChartData() {
        fetch(this.url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                this.renderChart(data);
            })
            .catch(error => {
                console.error("Fetch failed:", error);
            });
    }

    calculatePoint(i, intervalSize, colorRangeInfo) {
        let { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
        return (useEndAsStart
            ? (colorEnd - (i * intervalSize))
            : (colorStart + (i * intervalSize)));
    }

    interpolateColors(dataLength, colorScale, colorRangeInfo) {
        let { colorStart, colorEnd } = colorRangeInfo;
        let colorRange = colorEnd - colorStart;
        let intervalSize = colorRange / dataLength;
        let i, colorPoint;
        let colorArray = [];

        for (i = 0; i < dataLength; i++) {
            colorPoint = this.calculatePoint(i, intervalSize, colorRangeInfo);
            colorArray.push(colorScale(colorPoint));
        }

        return colorArray;
    }
}