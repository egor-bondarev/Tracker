import React, { useState, useRef, useEffect } from 'react';

const ColumnSelector: React.FC<{ columns: string[], visibleColumns: string[], onToggleColumn: (column: string) => void}> = ({ columns, visibleColumns, onToggleColumn }) => {
    const [isOpen, setIsOpen] = useState(false);

    const containerFilterMenuRef = useRef<HTMLDivElement>(null);

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    const closeFilterMenu = () => {
        setIsOpen(false);
    };

    const handleClickOutside = (event: MouseEvent) => {
        if (containerFilterMenuRef.current && !containerFilterMenuRef.current.contains(event.target as Node)) {
            closeFilterMenu()
        }
    }
    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="column-selector">
            <button onClick={toggleMenu} className='App-page-result-settings-filter-button'>Select Columns</button>
            {isOpen && (
                <div className="menu" ref={containerFilterMenuRef}>
                    {columns.map(column => (
                        <div key={column}>
                            <input
                                type="checkbox"
                                id={column}
                                checked={visibleColumns.includes(column)}
                                onChange={() => onToggleColumn(column)}
                            />
                            <label htmlFor={column}>{column}</label>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ColumnSelector;