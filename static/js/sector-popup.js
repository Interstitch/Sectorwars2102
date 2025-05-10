
function initializeSectorPopup(event, d) {
    const popup = document.createElement('div');
    popup.className = 'sector-info';
    popup.style.position = 'fixed';
    popup.style.left = `${event.pageX + 20}px`;
    popup.style.top = `${event.pageY}px`;
    popup.style.background = 'rgba(40, 40, 40, 0.95)';
    popup.style.borderRadius = '8px';
    popup.style.zIndex = '1000';

    async function updateSectorData(field, value) {
        try {
            const response = await fetch('/admin/update_sector', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sector_id: d.id,
                    field: field,
                    value: value
                })
            });
            if (!response.ok) throw new Error('Update failed');
            return await response.json();
        } catch (err) {
            console.error('Failed to update:', err);
            return null;
        }
    }

    async function updatePortData(type, item, value) {
        try {
            const response = await fetch('/admin/update_sector', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sector_id: d.id,
                    field: `port_${type}`,
                    item: item,
                    value: value
                })
            });
            if (!response.ok) throw new Error('Update failed');
            if (!d.port) d.port = {inventory: {}, buy: {}, sell: {}};
            d.port[type][item] = value;
        } catch (err) {
            console.error('Failed to update:', err);
        }
    }

    popup.innerHTML = `
        <h3>Sector ${d.id} - ${d.name}</h3>
        <div class="edit-group">
            <label>Has Planet</label>
            <input type="checkbox" ${d.has_planet ? 'checked' : ''} 
                   onchange="updateSectorData('has_planet', this.checked)">
        </div>
        <div class="edit-group">
            <label>Planet Fighters: ${d.planet_fighters || 0}</label>
            <input type="range" min="0" max="1000" step="5"
                   value="${d.planet_fighters || 0}"
                   oninput="this.nextElementSibling.value = this.value"
                   onchange="updateSectorData('planet_fighters', Number(this.value))">
            <output>${d.planet_fighters || 0}</output>
        </div>
        <button onclick="this.parentElement.remove()" class="close-btn">Close</button>
    `;

    document.body.appendChild(popup);
}
