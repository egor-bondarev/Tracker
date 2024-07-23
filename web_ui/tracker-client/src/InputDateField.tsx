import React, { forwardRef, ChangeEvent } from 'react';

interface InputDateTimeFieldProps {
    value: string;
    onClick: any;
    onChange: (event: ChangeEvent<HTMLInputElement>) => void;
    className: string
}

const CustomInputDateTime = forwardRef<HTMLInputElement, InputDateTimeFieldProps>(({ value, onClick, onChange, className }, ref) => (
    <div className={className}>
        <input
            type="text"
            value={value}
            readOnly={false}
            onClick={onClick}
            onChange={onChange}
            ref={ref}
        />
        <div className="icon" onClick={onClick}></div>
    </div>
));

export default CustomInputDateTime;
