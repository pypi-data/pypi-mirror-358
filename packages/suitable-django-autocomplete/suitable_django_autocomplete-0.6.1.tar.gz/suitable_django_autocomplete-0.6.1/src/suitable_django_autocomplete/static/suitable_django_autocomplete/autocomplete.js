class AutocompleteInput extends HTMLElement {
    static formAssociated = true;
    
    constructor() {
        super();
        this.debounceTimeout = null;
        this.debounceDelay = 300;
        this.minLength = 2;
        this.activeIndex = -1;
        this.results = [];
        this.selectedItem = null;
        this.valueField = this.getAttribute('data-value-field') || 'value';
        this.labelField = this.getAttribute('data-label-field') || 'label';
        this.originalPlaceholder = '';
        
        this._internals = this.attachInternals();
        
        this.input = this.shadowRoot.querySelector('input');
        this.resultsContainer = this.shadowRoot.querySelector('.results');
        
        // Store original placeholder
        this.originalPlaceholder = this.input.getAttribute('placeholder') || '';
        
        // hoist aria from host → internal input for naming & description
        const ariaLabel = this.getAttribute('aria-label');
        const ariaLabelledBy = this.getAttribute('aria-labelledby');
        const ariaDescribedBy = this.getAttribute('aria-describedby');
        if (ariaLabel)       { this._internals.ariaLabel = ariaLabel;
                               this.input.setAttribute('aria-label', ariaLabel); }
        if (ariaLabelledBy)  this.input.setAttribute('aria-labelledby', ariaLabelledBy);
        
        // Set up aria-describedby to include both external and internal descriptions
        const describedByIds = [];
        if (ariaDescribedBy) describedByIds.push(ariaDescribedBy);
        describedByIds.push(this.statusId);
        this.input.setAttribute('aria-describedby', describedByIds.join(' '));

        this.setupAccessibility();
        this.setupEventListeners();
        this.handleInitialValue();
    }
    
    setupAccessibility() {
        // Generate unique IDs for ARIA relationships
        this.inputId = `autocomplete-input-${Math.random().toString(36).substr(2, 9)}`;
        this.listboxId = `autocomplete-listbox-${Math.random().toString(36).substr(2, 9)}`;
        this.statusId = `autocomplete-status-${Math.random().toString(36).substr(2, 9)}`;
        
        // Set ARIA attributes on input
        this.input.setAttribute('id', this.inputId);
        
        // Put structural ARIA on the host so label → host works
        this.setAttribute('role', 'combobox');
        this.setAttribute('aria-autocomplete', 'list');
        this.setAttribute('aria-expanded', 'false');
        this.setAttribute('aria-controls', this.listboxId);
        this.setAttribute('aria-haspopup', 'listbox');
        
        // Set ARIA attributes on results container
        this.resultsContainer.setAttribute('id', this.listboxId);
        this.resultsContainer.setAttribute('role', 'listbox');
        this.resultsContainer.setAttribute('aria-label', 'Autocomplete suggestions');
        
        // Set up the status element for aria-describedby
        const statusElement = this.shadowRoot.querySelector('.sr-only');
        if (statusElement) {
            statusElement.setAttribute('id', this.statusId);
        }
    }
    
    setupEventListeners() {
        this.input.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
            // Clear selected item if user types manually
            if (this.selectedItem && e.target.value !== this.getItemLabel(this.selectedItem)) {
                this.selectedItem = null;
                this.updateFormValue('');
            }
            
            // Propagate input event to host element
            this.dispatchEvent(new InputEvent('input', {
                bubbles: true,
                cancelable: true,
                data: e.data,
                inputType: e.inputType
            }));
        });
        
        this.input.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
            
            // Propagate keydown event to host element
            this.dispatchEvent(new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                key: e.key,
                code: e.code,
                keyCode: e.keyCode,
                shiftKey: e.shiftKey,
                ctrlKey: e.ctrlKey,
                altKey: e.altKey,
                metaKey: e.metaKey
            }));
        });
        
        this.input.addEventListener('focus', (e) => {
            if (this.input.value.length >= this.minLength) {
                this.showResults();
            }
            
            // Propagate focus event to host element
            this.dispatchEvent(new FocusEvent('focus', {
                bubbles: true,
                cancelable: true
            }));
        });
        
        this.input.addEventListener('blur', (e) => {
            // Don't hide if clicking on a result item
            if (e.relatedTarget && this.resultsContainer.contains(e.relatedTarget)) {
                return;
            }
            
            // Propagate blur event to host element
            this.dispatchEvent(new FocusEvent('blur', {
                bubbles: true,
                cancelable: true,
                relatedTarget: e.relatedTarget
            }));
            
            setTimeout(() => {
                this.hideResults();
                // Clear value if no valid selection
                if (!this.selectedItem && this.input.value) {
                    this.input.value = '';
                    this.updateFormValue('');
                }
            }, 150);
        });
        
        
        document.addEventListener('click', (e) => {
            if (!this.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    handleInput(value) {
        clearTimeout(this.debounceTimeout);
        
        if (value.length < this.minLength) {
            this.hideResults();
            return;
        }
        
        this.debounceTimeout = setTimeout(() => {
            this.fetchResults(value);
        }, this.debounceDelay);
    }
    
    async fetchResults(query) {
        const endpoint = this.getAttribute('endpoint');
        if (!endpoint) {
            console.error('No endpoint attribute specified');
            this.showError('Configuration error: No endpoint specified');
            return;
        }
        
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        try {
            this.showLoading();
            
            const url = new URL(endpoint, window.location.origin);
            url.searchParams.append('q', query);
            
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Validate response structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            this.renderResults(data.results || []);
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                console.error('Request timeout');
                this.showError('Request timed out. Please try again.');
            } else if (error.message.includes('HTTP error')) {
                console.error('HTTP error:', error);
                this.showError('Server error. Please try again later.');
            } else if (error instanceof TypeError) {
                console.error('Network error:', error);
                this.showError('Network error. Please check your connection.');
            } else {
                console.error('Fetch error:', error);
                this.showError('Failed to fetch results');
            }
        }
    }
    
    showLoading() {
        this.resultsContainer.innerHTML = '<div class="loading">Loading...</div>';
        this.showResults();
        this.updateStatus('Loading suggestions');
    }
    
    showError(message) {
        this.resultsContainer.innerHTML = `<div class="loading">${message}</div>`;
        this.showResults();
        this.updateStatus(message);
    }
    
    renderResults(results) {
        this.results = results;
        this.activeIndex = -1;

        if (results.length === 0) {
            this.resultsContainer.innerHTML =
                '<div class="loading">No results found</div>';
            this.showResults();
            // Update status for aria-describedby
            this.updateStatus('No results found');
            return;
        }

        // build options ⬇
        const html = results.map((result, index) => {
            const displayText = this.getItemLabel(result);
            const optionId    = `${this.listboxId}-option-${index}`;
            return `<div class="result-item"
                         role="option"
                         id="${optionId}"
                         data-index="${index}"
                         tabindex="-1"
                         aria-selected="false">${this.escapeHtml(displayText)}</div>`;
        }).join('');

        this.resultsContainer.innerHTML = html;

        this.resultsContainer.querySelectorAll('.result-item')
            .forEach((item, index) => item.addEventListener('click',
                () => this.selectResultByIndex(index)));

        this.showResults();

        // Update status for aria-describedby
        this.updateStatus(`${this.results.length} suggestion${this.results.length !== 1 ? 's' : ''} available`);
    }

    
    selectResultByIndex(index) {
        console.log("selectResultByIndex", index)
        if (index >= 0 && index < this.results.length) {
            const item = this.results[index];
            this.selectedItem = item;
            const label = this.getItemLabel(item);
            const value = this.getItemValue(item);
            
            this.input.value = label;
            this.updateFormValue(value);
            this.hideResults();
            
            this.dispatchEvent(new CustomEvent('autocomplete-select', {
                detail: { value, label, item },
                bubbles: true
            }));
            this.dispatchEvent(new Event('change', {
                bubbles: true,
                cancelable: true
            }));
        }
    }
    
    updateFormValue(value) {
        this._internals.setFormValue(value);
    }
    
    get name() {
        return this.getAttribute('name');
    }
    
    handleKeyDown(e) {
        const isResultsVisible = this.resultsContainer.style.display === 'block';
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (!isResultsVisible && this.input.value.length >= this.minLength) {
                    this.fetchResults(this.input.value);
                } else if (this.results.length > 0) {
                    this.moveActiveIndex(1);
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (this.results.length > 0) {
                    this.moveActiveIndex(-1);
                }
                break;
                
            case 'Enter':
                if (isResultsVisible && this.activeIndex >= 0) {
                    e.preventDefault();
                    this.selectActiveResult();
                }
                break;
                
            case 'Escape':
                if (isResultsVisible) {
                    e.preventDefault();
                    this.hideResults();
                    this.input.focus();
                }
                break;
                
            case 'Tab':
                if (isResultsVisible) {
                    this.hideResults();
                }
                break;
        }
    }
    
    moveActiveIndex(direction) {
        const maxIndex = this.results.length - 1;
        
        if (direction > 0) {
            this.activeIndex = this.activeIndex < maxIndex ? this.activeIndex + 1 : 0;
        } else {
            this.activeIndex = this.activeIndex > 0 ? this.activeIndex - 1 : maxIndex;
        }
        
        this.updateActiveDescendant();
    }
    
    updateActiveDescendant() {
        // Clear previous selection
        this.resultsContainer.querySelectorAll('.result-item').forEach(item => {
            item.setAttribute('aria-selected', 'false');
            item.classList.remove('active');
        });
        
        if (this.activeIndex >= 0) {
            const activeItem = this.resultsContainer.querySelector(`[data-index="${this.activeIndex}"]`);
            if (activeItem) {
                activeItem.setAttribute('aria-selected', 'true');
                activeItem.classList.add('active');
                this.input.setAttribute('aria-activedescendant', activeItem.id);
                
                // Scroll into view if needed
                activeItem.scrollIntoView({ block: 'nearest' });
            }
        } else {
            this.input.removeAttribute('aria-activedescendant');
        }
    }
    
    selectActiveResult() {
        if (this.activeIndex >= 0 && this.results[this.activeIndex]) {
            this.selectResultByIndex(this.activeIndex);
        }
    }
    
    showResults() {
        this.resultsContainer.style.display = 'block';
        this.setAttribute('aria-expanded', 'true');
        // Clear placeholder when showing results to avoid confusion
        this.input.setAttribute('placeholder', '');
    }
    
    hideResults() {
        this.resultsContainer.style.display = 'none';
        this.setAttribute('aria-expanded', 'false');
        this.input.removeAttribute('aria-activedescendant');
        this.activeIndex = -1;
        // Restore placeholder when hiding results
        this.input.setAttribute('placeholder', this.originalPlaceholder);
        // Clear status
        this.updateStatus('');
    }
    
    updateStatus(message) {
        const statusElement = this.shadowRoot.querySelector(`#${this.statusId}`);
        if (statusElement) {
            statusElement.textContent = message;
        }
    }
    
    getItemLabel(item) {
        if (typeof item === 'string') {
            return item;
        }
        // Try common label fields
        return item[this.labelField] || item.label || item.name || item.title || item.text || String(item.value || '');
    }
    
    getItemValue(item) {
        if (typeof item === 'string') {
            return item;
        }
        // Try common value fields
        return item[this.valueField] || item.value || item.id || this.getItemLabel(item);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    handleInitialValue() {
        const initialValue = this.getAttribute('value');
        const displayValue = this.getAttribute('data-display-value');
        
        if (initialValue) {
            this._internals.setFormValue(initialValue);
            if (displayValue) {
                this.input.value = displayValue;
                // Create a temporary selected item
                this.selectedItem = {
                    [this.valueField]: initialValue,
                    [this.labelField]: displayValue
                };
            }
        }
    }
    
    // Override value getter/setter to handle initial binding
    get value() {
        return this.selectedItem ? this.getItemValue(this.selectedItem) : '';
    }
    
    set value(val) {
        if (val) {
            // Store the initial value and try to resolve it when we get results
            this.initialValue = val;
            this._internals.setFormValue(val);
        } else {
            this.input.value = '';
            this.selectedItem = null;
            this.updateFormValue('');
        }
    }
}

customElements.define('autocomplete-input', AutocompleteInput);