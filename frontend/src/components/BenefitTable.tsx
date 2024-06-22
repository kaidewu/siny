import React, { useState } from 'react';
import { Benefit, Filter } from '../types';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const BenefitTable: React.FC = () => {
  const [benefits, setBenefits] = useState<Benefit[]>([]);
  const [filter, setFilter] = useState<Filter>({
    benefit_name: '',
    benefit_code: '',
    benefit_type_code: '',
    benefit_subtype_code: '',
    active: true,
    start_created_date: '',
    end_created_date: '',
    deleted: false
  });

  const fetchBenefits = async () => {
    try {
      const url = `http://localhost:8080/api/v1/benefits?${new URLSearchParams(filter as any).toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setBenefits(data);
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setFilter({ ...filter, [name]: value });
  };

   const handleDateChange = (date: Date | null, field: 'start_created_date' | 'end_created_date') => {
    if (date) {
      setFilter({ ...filter, [field]: date.toISOString().split('T')[0] });
    } else {
      setFilter({ ...filter, [field]: '' });
    }
  };

  const handleApplyFilter = () => {
    fetchBenefits();
  };

  return (
    <div>
      <div style={{ display: 'flex', marginBottom: '1rem' }}>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Benefit Name:
            <input type="text" name="benefit_name" value={filter.benefit_name} onChange={handleInputChange} />
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Benefit Code:
            <input type="text" name="benefit_code" value={filter.benefit_code} onChange={handleInputChange} />
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Benefit Type Code:
            <input type="text" name="benefit_type_code" value={filter.benefit_type_code} onChange={handleInputChange} />
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Benefit Subtype Code:
            <input type="text" name="benefit_subtype_code" value={filter.benefit_subtype_code} onChange={handleInputChange} />
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Active:
            <select name="active" value="Active" onChange={handleInputChange}>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Deleted:
            <select name="deleted" value="Not Deleted" onChange={handleInputChange}>
                <option value="false">Not Deleted</option>
              <option value="true">Deleted</option>
            </select>
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            Start Created Date:
            <DatePicker
              selected={filter.start_created_date ? new Date(filter.start_created_date) : null}
              onChange={(date) => handleDateChange(date, 'start_created_date')}
              dateFormat="yyyy-MM-dd"
            />
          </label>
        </div>
        <div style={{ marginRight: '1rem' }}>
          <label>
            End Created Date:
            <DatePicker
              selected={filter.end_created_date ? new Date(filter.end_created_date) : null}
              onChange={(date) => handleDateChange(date, 'end_created_date')}
              dateFormat="yyyy-MM-dd"
            />
          </label>
        </div>
      </div>
      <button onClick={handleApplyFilter}>Apply Filter</button>

      <table>
        <thead>
          <tr>
            <th>Benefit Name</th>
            <th>Benefit Code</th>
            <th>Benefit Type Name</th>
            <th>Benefit Subtype Name</th>
            <th>Is Active</th>
            <th>Active Date</th>
            <th>Created Date</th>
            <th>Is Deleted</th>
            <th>Deleted Date</th>
          </tr>
        </thead>
        <tbody>
          {benefits.map((benefit, index) => (
            <tr key={index}>
              <td>{benefit.benefitName}</td>
              <td>{benefit.benefitCode}</td>
              <td>{benefit.benefitTypeName}</td>
              <td>{benefit.benefitSubtypeName}</td>
              <td>{benefit.isActive ? 'Yes' : 'No'}</td>
              <td>{benefit.activeDate}</td>
              <td>{benefit.createdDate}</td>
              <td>{benefit.isDeleted ? 'Yes' : 'No'}</td>
              <td>{benefit.deletedDate}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BenefitTable;