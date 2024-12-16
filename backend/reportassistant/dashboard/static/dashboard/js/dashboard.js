class DashboardHelper {
    constructor(titleElementId,
                dashboardTitleValidationErrorId,
                gridContainerId,
                createDashboardUrl,
                dashboard_url,
                dashboard_slot_url,
                updateSlotsUrl
    ) {
        GridStack.renderCB = function(el, w) {
            el.innerHTML = w.content;
        };
        this.titleElement = document.getElementById(titleElementId);
        this.dashboardTitleValidationError = document.getElementById(dashboardTitleValidationErrorId);
        this.gridContainerId = gridContainerId;
        this.grid = null;
        this.createDashboardUrl = createDashboardUrl
        this.dashboard_url = dashboard_url
        this.dashboard_slot_url = dashboard_slot_url
        this.updateSlotsUrl = updateSlotsUrl
    }

    resetErrors() {
        this.titleElement.classList.remove('is-invalid');
        this.dashboardTitleValidationError.style.display = 'None';
    }

    async createDashboard() {
        this.resetErrors();
        const title = this.titleElement.value;
        try {
            if (!title) {
                this.dashboardTitleValidationError.style.display = 'block';
                this.titleElement.classList.add("is-invalid");
                return;
            }

            const response = await fetch(this.createDashboardUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': Cookies.get('csrftoken')
                },
                body: new URLSearchParams({
                    title: title
                })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById("DashboardModalClose").click();
                console.log('Dashboard created successfully:', data);
                await this.getDashboardOptions(this.dashboard_url);
                return data;
            } else {
                const errorData = await response.json();
                console.error('Failed to create dashboard:', errorData);
                throw new Error(errorData.error || 'Failed to create dashboard');
            }
        } catch (error) {
            console.error('An error occurred:', error.message);
            throw error;
        }
    }

    async getDashboardOptions() {
        try {
            const response = await fetch(this.dashboard_url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': Cookies.get('csrftoken')
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load dashboards');
            }

            const data = await response.json();

            // Get the select element
            const selectElement = document.getElementById('existingDashboards');

            // Clear any existing options
            selectElement.innerHTML = '';

            // Populate the select element with the dashboards
            data.forEach(dashboard => {
                const option = document.createElement('option');
                option.value = dashboard.id;
                option.textContent = dashboard.title;
                selectElement.appendChild(option);
            });

            // Set the first dashboard as the default selection
            if (data.length > 0) {
                selectElement.value = data[0].id;
                await this.fetchDashboardData(data[0].id);
            }

        } catch (error) {
            console.error('Error loading dashboards:', error);
        }
    }

    async fetchDashboardData(id) {
        try {
            const response = await fetch(this.dashboard_slot_url.replace('0', id), {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': Cookies.get('csrftoken')
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load data');
            }

            const data = await response.json();
            this.initGridStack(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    initGridStack(data) {
        let children = data.map(slot => {
            return {
                x: slot.col_num,
                y: slot.row_num,
                w: slot.width,
                h: slot.height,
                content: `<div class="slot-content">Slot ID: ${slot.id}</div>`,
                slot_id: slot.id
            };
        });

        console.log(children);

        if (this.grid) {
            this.grid.destroy();
            this.grid = null;
        }

        if (children.length === 0) {
            return;
        }

        const gridStackElement = document.createElement("div");
        gridStackElement.classList.add("grid-stack");
        document.getElementById(this.gridContainerId).appendChild(gridStackElement);

        this.grid = GridStack.init({ children });

        this.grid.on('change', () => {
            const slots = this.grid.save();
            console.log(slots);
            this.updateDashboardSlots(slots)
        });
    }

     updateDashboardSlots(slots) {
            fetch(this.updateSlotsUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Specify the content type
                    'X-CSRFToken':  Cookies.get('csrftoken'),
                },
                body: JSON.stringify({ slots: slots })
            })
            .catch(error => {
                console.error('Request failed', error);
            });
    }
}
