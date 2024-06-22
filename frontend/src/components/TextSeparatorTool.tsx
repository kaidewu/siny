import React, { useState } from 'react';

const TextSeparatorTool: React.FC = () => {
    const [inputText, setInputText] = useState('');
    const [separatorOption, setSeparatorOption] = useState('');
    const [result, setResult] = useState('');

    const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputText(event.target.value);
    };

    const handleSeparatorChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSeparatorOption(event.target.value);
    };

    const handleFormSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        // Split inputText by newline characters
        const lines = inputText.split('\n').filter(line => line.trim() !== '');

        // Apply the selected separator
        let separatorStart = '';
        let separatorEnd = '';
        if (separatorOption === "simple") {
            separatorStart = "'";
            separatorEnd = "'";
        } else if (separatorOption === "double") {
            separatorStart = '"';
            separatorEnd = '"';
        } else if (separatorOption === "nothing") {
            separatorStart = '';
            separatorEnd = '';
        }

        const separatedContent = lines.map(line => `${separatorStart}${line}${separatorEnd}`).join(', ');
        setResult(separatedContent);
    };

    const handleCopyToClipboard = () => {
        navigator.clipboard.writeText(result);
    };

    return (
        <div className="container mx-auto mt-8">
            <h1 className="text-3xl font-semibold mb-4">Text Separator Tool</h1>
            <form onSubmit={handleFormSubmit}>
                <div className="mb-4">
                    <label htmlFor="textInput" className="block text-sm font-medium text-gray-700 mb-1">Enter Text:</label>
                    <textarea
                        id="textInput"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                        rows={6}
                        value={inputText}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div className="mb-4">
                    <label htmlFor="separatorOption" className="block text-sm font-medium text-gray-700 mb-1">Select Separator Option:</label>
                    <select
                        id="separatorOption"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                        value={separatorOption}
                        onChange={handleSeparatorChange}
                        required
                    >
                        <option value="nothing">Nothing</option>
                        <option value="simple">Simple ('')</option>
                        <option value="double">Double ("")</option>
                    </select>
                </div>
                <div className="mb-4">
                    <button
                        type="submit"
                        className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
                    >
                        GO
                    </button>
                </div>
            </form>
            {result && (
                <div className="mt-6 border border-gray-300 rounded-md p-4 bg-gray-100">
                    <h2 className="text-lg font-semibold mb-2">Result:</h2>
                    <div className="mb-2">
                        <textarea
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                            rows={3}
                            value={result}
                            readOnly
                        />
                    </div>
                    <button
                        className="bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
                        onClick={handleCopyToClipboard}
                    >
                        Copy Result
                    </button>
                </div>
            )}
        </div>
    );
};

export default TextSeparatorTool;
