import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://obscure-halibut-jvrwqwpjwqwcpv7r-8000.app.github.dev/api/students/';
function App() {
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState({
    student_id: '', first_name: '', last_name: '', email: '',
    phone: '', date_of_birth: '', gender: 'M', course: '',
    year_of_study: 1, gpa: 0, status: 'ACTIVE'
  });
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Sab students fetch karo
  const fetchStudents = async () => {
    const res = await axios.get(API_URL);
    setStudents(res.data);
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  // Form change handle
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Submit form (Add/Update)
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editingId) {
      await axios.put(`${API_URL}${editingId}/`, form);
      alert('Student Updated!');
    } else {
      await axios.post(API_URL, form);
      alert('Student Added!');
    }
    setForm({ student_id: '', first_name: '', last_name: '', email: '', phone: '', date_of_birth: '', gender: 'M', course: '', year_of_study: 1, gpa: 0, status: 'ACTIVE' });
    setEditingId(null);
    setShowForm(false);
    fetchStudents();
  };

  // Delete student
  const handleDelete = async (id) => {
    if (window.confirm('Delete this student?')) {
      await axios.delete(`${API_URL}${id}/`);
      fetchStudents();
    }
  };

  // Edit student
  const handleEdit = (student) => {
    setForm(student);
    setEditingId(student.id);
    setShowForm(true);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1 style={{ textAlign: 'center', color: 'blue' }}>📚 Student Management System</h1>
      
      {/* Buttons */}
      <div style={{ margin: '20px 0', textAlign: 'center' }}>
        {!showForm ? (
          <button onClick={() => setShowForm(true)} style={{ padding: '10px 20px', background: 'green', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            ➕ Add New Student
          </button>
        ) : (
          <button onClick={() => { setShowForm(false); setEditingId(null); }} style={{ padding: '10px 20px', background: 'gray', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            ❌ Cancel
          </button>
        )}
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div style={{ border: '2px solid blue', padding: '20px', margin: '20px 0', borderRadius: '10px', background: '#f0f0f0' }}>
          <h2>{editingId ? '✏️ Edit Student' : '➕ Add New Student'}</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <input name="student_id" placeholder="Student ID (e.g., STU001)" value={form.student_id} onChange={handleChange} required style={inputStyle} />
              <input name="first_name" placeholder="First Name" value={form.first_name} onChange={handleChange} required style={inputStyle} />
              <input name="last_name" placeholder="Last Name" value={form.last_name} onChange={handleChange} required style={inputStyle} />
              <input name="email" placeholder="Email" type="email" value={form.email} onChange={handleChange} required style={inputStyle} />
              <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} required style={inputStyle} />
              <input name="date_of_birth" placeholder="Date of Birth (YYYY-MM-DD)" type="date" value={form.date_of_birth} onChange={handleChange} required style={inputStyle} />
              <select name="gender" value={form.gender} onChange={handleChange} style={inputStyle}>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
              <input name="course" placeholder="Course" value={form.course} onChange={handleChange} required style={inputStyle} />
              <input name="year_of_study" placeholder="Year of Study (1-5)" type="number" value={form.year_of_study} onChange={handleChange} required style={inputStyle} />
              <input name="gpa" placeholder="GPA (0-4)" type="number" step="0.01" value={form.gpa} onChange={handleChange} required style={inputStyle} />
              <select name="status" value={form.status} onChange={handleChange} style={inputStyle}>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </div>
            <button type="submit" style={{ marginTop: '20px', padding: '10px 20px', background: 'blue', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
              {editingId ? 'Update Student' : 'Add Student'}
            </button>
          </form>
        </div>
      )}

      {/* Students Table */}
      <h2>📋 Student List ({students.length} students)</h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: 'blue', color: 'white' }}>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Name</th>
              <th style={thStyle}>Email</th>
              <th style={thStyle}>Course</th>
              <th style={thStyle}>Year</th>
              <th style={thStyle}>GPA</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={tdStyle}>{student.student_id}</td>
                <td style={tdStyle}>{student.first_name} {student.last_name}</td>
                <td style={tdStyle}>{student.email}</td>
                <td style={tdStyle}>{student.course}</td>
                <td style={tdStyle}>{student.year_of_study}</td>
                <td style={tdStyle}>
                  <span style={{ background: student.gpa >= 3.5 ? 'green' : student.gpa >= 2.5 ? 'orange' : 'red', color: 'white', padding: '3px 8px', borderRadius: '5px' }}>
                    {student.gpa}
                  </span>
                </td>
                <td style={tdStyle}>
                  <span style={{ background: student.status === 'ACTIVE' ? 'green' : 'gray', color: 'white', padding: '3px 8px', borderRadius: '5px' }}>
                    {student.status}
                  </span>
                </td>
                <td style={tdStyle}>
                  <button onClick={() => handleEdit(student)} style={{ background: 'orange', color: 'white', border: 'none', padding: '5px 10px', margin: '0 5px', borderRadius: '3px', cursor: 'pointer' }}>Edit</button>
                  <button onClick={() => handleDelete(student.id)} style={{ background: 'red', color: 'white', border: 'none', padding: '5px 10px', margin: '0 5px', borderRadius: '3px', cursor: 'pointer' }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const inputStyle = {
  padding: '8px',
  border: '1px solid #ccc',
  borderRadius: '5px',
  fontSize: '14px'
};

const thStyle = {
  padding: '12px',
  textAlign: 'left',
  borderBottom: '2px solid white'
};

const tdStyle = {
  padding: '10px',
  textAlign: 'left'
};

export default App;