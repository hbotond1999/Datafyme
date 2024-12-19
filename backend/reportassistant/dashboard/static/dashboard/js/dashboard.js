class DashboardHelper {
    constructor(titleElementId,
                dashboardTitleValidationErrorId,
                gridContainerId,
                createDashboardUrl,
                dashboard_url,
                dashboard_slot_url,
                updateSlotsUrl,
                deleteDashboardSlotUrl,
                deleteDashboardUrl
    ) {
        GridStack.renderCB = (el, w)=> {
            el.appendChild(this.createGirdContent(w.data))
        };
        this.titleElement = document.getElementById(titleElementId);
        this.dashboardTitleValidationError = document.getElementById(dashboardTitleValidationErrorId);
        this.gridContainerId = gridContainerId;
        this.grid = null;
        this.createDashboardUrl = createDashboardUrl
        this.dashboard_url = dashboard_url
        this.dashboard_slot_url = dashboard_slot_url
        this.updateSlotsUrl = updateSlotsUrl
        this.deleteDashboardSlotUrl = deleteDashboardSlotUrl
        this.deleteDashboardUrl = deleteDashboardUrl

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
                await this.getDashboardOptions();
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

    async fetchDashboardData() {
        try {
            const dashboardId = document.getElementById("existingDashboards").value
            if (!dashboardId) {
                this.initGridStack([]);
                return
            }
            const response = await fetch(this.dashboard_slot_url.replace('0', dashboardId), {
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
            this.initGridStack([])
        }
    }

    initGridStack(data) {
        let children = data.map(slot => {
            return {
                x: slot.col_num,
                y: slot.row_num,
                w: slot.width,
                h: slot.height,
                data: slot,
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

        this.grid = GridStack.init({ children, margin: '6px'});

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

   createGirdContent(slot) {

        const slotContainer = document.createElement("div");
        slotContainer.className = "slot-container";
        slotContainer.dataset.slotId = slot.id;

        const slotHeader = document.createElement("div");
        slotHeader.className = "slot-header";

        const slotTitle = document.createElement("h3");
        slotTitle.textContent = slot.id;

        const trashIconContainer = document.createElement("div");
        const trashIcon = document.createElement("i");
        trashIcon.className = "fas fa-trash slot-trash";
        trashIcon.addEventListener("click", () => this.deleteDashboardSlot(slot.id));
        trashIconContainer.appendChild(trashIcon);
        slotHeader.appendChild(slotTitle);
        slotHeader.appendChild(trashIconContainer);
        slotContainer.appendChild(slotHeader);
        return slotContainer
   }

   deleteDashboardSlot(id) {
    const url = this.deleteDashboardSlotUrl.replace('0', id)

    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken':  Cookies.get('csrftoken'),
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(() => {
        this.fetchDashboardData().then()
    })
    .catch(error => {
        console.error("Error deleting slot:", error);
    });
}

   deleteDashboard() {
   const dashboardId = document.getElementById("existingDashboards").value
    if (!dashboardId) {
        return
    }
    fetch(this.deleteDashboardUrl.replace('0', dashboardId), {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken':  Cookies.get('csrftoken'),
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        this.getDashboardOptions().then(() => this.fetchDashboardData().then());

    })
    .catch(error => {
        console.error("Error deleting slot:", error);
    });
}
}
