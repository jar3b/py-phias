function showError(errText = '') {
    const errorElem = document.getElementById("error");
    errorElem.hidden = !errText;
    errorElem.innerText = errText;
}

function createResultElem(template, data) {
    const el = template.cloneNode(true);
    el.removeAttribute('id');
    el.querySelector("input").id = `tab-${data.aoid}`;
    el.querySelector("label").setAttribute('for', `tab-${data.aoid}`);
    el.querySelector("label").prepend(document.createTextNode(data.text));
    el.querySelector("label span").textContent = `${data.ratio} [${data.cort}]`;
    el.querySelector(".tab-content p").textContent = `AOID: ${data.aoid}`;

    return el;
}

function clearResults(results) {
    results.innerHTML = '';
}

async function searchAddress(text, results, template) {
    try {
        const data = await fetch(`${window.apiPrefix}/find/${text}`);
        if (!data.ok) {
            return showError(`${data.status}: ${(await data.json()).error ?? 'Unknown error'}`)
        }

        const arr = await data.json();
        arr.forEach((value, i, a) => {
            results.appendChild(createResultElem(template, value));
        })
    } catch (e) {
        showError(e);
    }
}

async function ready() {
    const searchInput = document.getElementById('fias-addr-search');
    const searchBtn = document.getElementById('search-btn');
    const resultsElem = document.getElementById('results');
    const templateSearchResElem = document.getElementById('tab-template').cloneNode(true);
    templateSearchResElem.hidden = false;

    searchInput.addEventListener('focus', (event) => {
        const doc = document.querySelector("input:checked");
        if (doc) doc.checked = false;
        showError();
    });

    searchBtn.addEventListener('click', async (event) => {
        clearResults(resultsElem);
        await searchAddress(searchInput.value, resultsElem, templateSearchResElem)
    });

    searchInput.addEventListener("keyup", function (event) {
        console.log(event, event.key);
        event.preventDefault();
        if (event.key === 'Enter') {
            searchBtn.click();
        }
    })
}

document.addEventListener("DOMContentLoaded", ready);