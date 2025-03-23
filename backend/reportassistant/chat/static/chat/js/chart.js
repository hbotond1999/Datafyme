class ChartHelper {
    constructor(url,
                chartUpdateUrl = '',
                generate_description_url = '',
                generateDescriptionCallback,
                parentContainer,
                chartId,
                draggable = false,
                scrollToInit = false,
                init = true
              ) {
        this.parent = parentContainer;
        this.url = url;
        this.chartId = chartId;

        this.chartUpdateUrl = chartUpdateUrl
        this.draggable = draggable
        this.scrollToInit = scrollToInit
        this.generate_description_url = generate_description_url
        this.generateDescriptionCallback = generateDescriptionCallback
        if (init) {
            this.init()
        }
    }

    renderChart(data) {
        if (data.type === "TABLE") {
            this.renderTable(data.chart_data, data.description);
        } else {
            this.renderCanvasChart(data);
        }
    }

    init () {
        this.getChartData();
    }

    renderCanvasChart(charData) {
        const canvas = document.createElement('canvas');
        if (this.draggable) {
            canvas.height = 300
            const contEl = this.createDraggableContainer()
            contEl.append(canvas);
            this.parent.append(contEl);
            setupDragIn()
        } else {
            const div = document.createElement("div")
            div.append(canvas)
            this.parent.append(div)
        }
        this.createChart(canvas, charData)
        if (this.scrollToInit) {
            canvas.scrollIntoView({behavior: "smooth", block: "end"})
        }
        console.log(charData)
        console.log("url", this.generate_description_url)
        if (this.generate_description_url) {
            setTimeout(() => {this.getDescription(canvas)}, 500)
        } else if (this.generateDescriptionCallback != null){
            this.generateDescriptionCallback(charData.description)
        }


    }

    createChart(canvas, charData) {
        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, charData.chart_data);
    }

    renderTable(tableData, description) {

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
        if (this.draggable) {
            const contEl = this.createDraggableContainer()
            contEl.append(table)
            this.parent.appendChild(contEl);
             setupDragIn()
        } else {
            this.parent.append(table)
        }

        if (this.scrollToInit) {
            table.scrollIntoView({behavior: "smooth"})
        }

        if (this.generate_description_url) {
            this.getDescription()
        } else if (this.generateDescriptionCallback != null){
            this.generateDescriptionCallback(description)
        }
    }

    createDraggableContainer() {
        const contEl = document.createElement("div");
        contEl.classList.add("grid-stack-item");
        contEl.classList.add("sidepanel-item");
        contEl.setAttribute("data-id", this.chartId)
        return contEl
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
    async updateChartTitle(newTitle) {
        try {
            const response = await fetch(this.chartUpdateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    'X-CSRFToken': Cookies.get('csrftoken'),
                },
                body: JSON.stringify({
                    id: this.chartId,
                    title: newTitle,
                }),
            });

            if (!response.ok) {
                console.error("Failed to update chart title.");
                return false;
            }

            return true;
        } catch (error) {
            console.error("Error while updating chart title:", error);
            return false;
        }
    }

   getDescription(canvas) {
        const formData = new FormData();
        formData.append("chart_id", this.chartId);

        if (canvas) {
            canvas.toBlob((blob) => {
                if (!blob) {
                    console.error("Canvas-to-blob conversion failed.");
                    this.sendDescriptionRequest(formData);
                    return;
                }
                formData.append("chart_img_file", blob, "chart.png");
                this.sendDescriptionRequest(formData);
            }, "image/png");
        } else {
            this.sendDescriptionRequest(formData);
        }
    }

    sendDescriptionRequest(formData) {
        fetch(this.generate_description_url, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get('csrftoken'),
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            this.generateDescriptionCallback(data.description);
            console.log("Generated Description:", data.description);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }
}