import api from './configs/axiosConfig';

export const ResumeParser = async (file) => {
  const res = await api.post('/resume-parser/', file);
  return res.data;
};

export const PredictStudent = async (data) => {
  const res = await api.post('/predict-student-placement/', data);
  return res.data;
};

export const RecommendSkills = async (data) => {
  const res = await api.post('/recommendSkills/', data);
  return res.data.recommended_skills || [];
};

export const DownloadRecommendedSkills = async (data) => {
  const response = await api.post('/recommendSkills/', data, {
    responseType: 'blob',
  });

  const blob = new Blob([response.data], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = 'recommended_skills.txt';
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};
