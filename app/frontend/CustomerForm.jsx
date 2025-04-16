import React, { useState } from 'react';
import axios from 'axios';

const defaultValues = {
  naming_series: "CUS-0001",
  salutation: "Mr.",
  customer_name: "John Doe",
  gender: "Male",
  customer_type: "Individual",
  default_bank_account: "HDFC-Current",
  lead_name: "LEAD-001",
  image: "",
  account_manager: "EMP-002",
  customer_group: "Retail",
  territory: "India",
  tax_id: "GSTIN1234ABCDE",
  tax_category: "Regular",
  disabled: false,
  is_internal_customer: false,
  represents_company: "Acme Corp",
  default_currency: "INR",
  default_price_list: "Standard Selling",
  language: "en",
  website: "https://customer-site.com",
  customer_primary_contact: "CNT-001",
  mobile_no: "+91-9876543210",
  email_id: "john.doe@example.com",
  customer_primary_address: "ADDR-001",
  primary_address: "123 Business Street, City, Country",
  payment_terms: "30 Days",
  customer_details: "Loyal customer from southern region",
  market_segment: "B2C",
  industry: "Retail",
  is_frozen: false,
  loyalty_program: "Gold",
  loyalty_program_tier: "Tier 1",
  default_sales_partner: "PARTNER-001",
  default_commission_rate: 5.0,
  customer_pos_id: "POS-CUST-001",
  so_required: false,
  dn_required: false,
  tax_withholding_category: "TDS",
  opportunity_name: "OPP-123",
  prospect_name: "Prospect Co.",
  id: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
};

const CustomerForm = () => {
  const [formData, setFormData] = useState(defaultValues);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log("Sending JSON to FastAPI:", formData);
      const response = await axios.post("http://127.0.0.1:8000/add_customer/", formData);
      alert("Customer added successfully!");
    } catch (error) {
      console.error("Submission error:", error);
      alert("Failed to add customer");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-6">Customer Form</h2>
      {Object.entries(formData).map(([key, value]) => (
        <div key={key} className="mb-4">
          <label className="block text-sm font-medium text-gray-700 capitalize">{key.replace(/_/g, ' ')}</label>
          {typeof value === "boolean" ? (
            <input
              type="checkbox"
              name={key}
              checked={value}
              onChange={handleChange}
              className="ml-2"
            />
          ) : (
            <input
              type="text"
              name={key}
              value={value}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          )}
        </div>
      ))}
      <button
        type="submit"
        className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition"
      >
        Submit
      </button>
    </form>
  );
};

export default CustomerForm;
