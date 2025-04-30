import { Fragment, useContext, useState } from 'react';
import { Header } from '../../components/header';
import { UploadBox } from '../campus/UploadBox';
import { motion } from 'framer-motion';
import {
    Alert,
    Button,
    CircularProgress,
    Container,
    IconButton,
    Snackbar,
} from '@mui/material';
import './resume.css';
import { RxCross2 } from 'react-icons/rx';
import CloseIcon from '@mui/icons-material/Close';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;




const ResumeUpload = () => {
    const [isResumeUpload, setIsResumeUpload] = useState(false);
    const [resumeParseLoading, setResumeParseLoading] = useState(false);
    const [studentName, setStudentName] = useState('');
    const [openSnackBar, setOpenSnackBar] = useState(false);
    const [score, setScore] = useState(null);
    const [resumeFile, setResumeFile] = useState(null);
    const [numPages, setNumPages] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [snackBarOptions, setSnackBarOptions] = useState({
        msg: '',
        severity: '',
    });

    const onDocumentLoadSuccess = ({ numPages }) => {
        setNumPages(numPages);
    };

    const handleOpenSnackBar = (msg, severity) => {
        setOpenSnackBar(true);
        setSnackBarOptions({ msg, severity });
    };

    const handleCloseSnackBar = (event, reason) => {
        if (reason === 'clickaway') return;
        setOpenSnackBar(false);
    };

    const action = (
        <Fragment>
            <Button color='secondary' size='small' onClick={handleCloseSnackBar}>
                UNDO
            </Button>
            <IconButton size='small' aria-label='close' color='inherit' onClick={handleCloseSnackBar}>
                <CloseIcon fontSize='small' />
            </IconButton>
        </Fragment>
    );

    const onUploadClick = async (file) => {
        if (!file) {
            handleOpenSnackBar('No file selected', 'error');
            return;
        }

        if (file.type !== 'application/pdf') {
            handleOpenSnackBar('Please upload a PDF file', 'error');
            return;
        }

        setResumeFile(file);
        const formData = new FormData();
        formData.append('resume', file);

        try {
            setResumeParseLoading(true);
            const res = await fetch('http://localhost:8000/ats/upload/', {
                method: 'POST',
                body: formData,
            });

            const data = await res.json();
            if (data.status === 'success') {
                setStudentName(data.name);
                setScore(data.score);
                setSuggestions(data.suggestions);
                handleOpenSnackBar('Resume parsed successfully!', 'success');
            } else {
                handleOpenSnackBar(data.message || 'Failed to parse resume', 'error');
            }
        } catch (err) {
            handleOpenSnackBar(err.message || 'Failed to parse resume', 'error');
        } finally {
            setResumeParseLoading(false);
        }
    };

    return (
        <div
            style={{
                fontFamily: 'var(--font-primary)',
                backgroundImage: 'linear-gradient(90deg, #21D4FD 0%, #cb8eeb 100%)',
                minHeight: '100vh',
            }}
        >
            <Header />

            <div style={{ minHeight: '90vh', height: 'fit-content', paddingBottom: '20px' }}>
                <Snackbar
                    open={openSnackBar}
                    autoHideDuration={6000}
                    onClose={handleCloseSnackBar}
                    action={action}
                >
                    <Alert onClose={handleCloseSnackBar} severity={snackBarOptions.severity}>
                        {snackBarOptions.msg}
                    </Alert>
                </Snackbar>

                <Container maxWidth='xl'>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '2rem' }}>
                        <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>
                            Upload Your Resume
                        </h1>

                        {!isResumeUpload ? (
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <div
                                    style={{
                                        padding: '1.2rem',
                                        border: '2px solid black',
                                        borderRadius: '40px',
                                        display: 'inline-block',
                                        cursor: 'pointer',
                                        margin: '10px',
                                        backgroundColor: 'rgba(0,0,0,0.1)',
                                    }}
                                    onClick={() => setIsResumeUpload(true)}
                                >
                                    Click to Upload Resume
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0.5, scale: 0 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                transition={{ type: 'spring', duration: 1 }}
                                style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}
                            >
                                {resumeParseLoading ? (
                                    <CircularProgress size='4rem' sx={{ color: '#000' }} />
                                ) : (
                                    <>
                                        <UploadBox acceptFiles='.pdf' onUploadClick={onUploadClick}>
                                            Upload your resume (PDF only)
                                        </UploadBox>
                                        <div
                                            style={{
                                                marginTop: '15px',
                                                cursor: 'pointer',
                                            }}
                                            onClick={() => setIsResumeUpload(false)}
                                        >
                                            <RxCross2 size={24} />
                                        </div>
                                    </>
                                )}
                            </motion.div>
                        )}
                    </div>

                    {studentName && resumeFile && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.5 }}
                            style={{
                                marginTop: '3rem',
                                display: 'flex',
                                gap: '2rem',
                                justifyContent: 'center',
                                alignItems: 'flex-start',
                                flexWrap: 'wrap',
                            }}
                        >
                            {/* Left - PDF Viewer */}
                            <div
                                style={{
                                    flex: '1 1 40%',
                                    minWidth: '300px',
                                    backgroundColor: '#fff',
                                    borderRadius: '10px',
                                    padding: '1rem',
                                }}
                            >
                                <Document
                                    file={resumeFile ? URL.createObjectURL(resumeFile) : null}
                                    onLoadSuccess={onDocumentLoadSuccess}
                                    onLoadError={(error)=>console.error("PDF load error:", error)}
                                    renderMode='canvas'
                                >
                                    {Array.from(new Array(numPages), (el, index) => (
                                        <Page
                                            key={`page_${index + 1}`}
                                            pageNumber={index + 1}
                                            width={400}
                                        />
                                    ))}
                                </Document>
                            </div>

                            {/* Right - Resume Details */}
                            <div
                                style={{
                                    flex: '1 1 50%',
                                    backgroundColor: 'rgba(255,255,255,0.3)',
                                    padding: '2rem',
                                    borderRadius: '20px',
                                    maxWidth: '700px',
                                }}
                            >
                                <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
                                    Hello, {studentName}!
                                </h2>
                                <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
                                    Your resume has been successfully processed.
                                </p>

                                {score !== null && (
                                    <p style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
                                        Resume Score: <span style={{ color: '#3f51b5' }}>{score}/100</span>
                                    </p>
                                )}

                                {suggestions.length > 0 && (
                                    <div style={{ textAlign: 'left', marginTop: '1rem' }}>
                                        <h3>Suggestions for Improvement:</h3>
                                        <ul style={{ paddingLeft: '1.5rem' }}>
                                            {suggestions.map((s, i) => (
                                                <li key={i} style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>
                                                    {s}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </Container>
            </div>
        </div>
    );
};

export default ResumeUpload;
