console.log('patients.js loaded successfully');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded');
    
    // Basic functionality to test
    const contentDiv = document.querySelector('.content');
    if (contentDiv) {
        const testParagraph = document.createElement('p');
        testParagraph.textContent = 'JavaScript is working!';
        contentDiv.appendChild(testParagraph);
    } else {
        console.error('Could not find .content div');
    }
});
