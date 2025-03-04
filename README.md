# OCRReader

OCR GUI based on Python and Qt6 designed to prepare and OCR images with complex layouts, mainly for Tesseract OCR.

## Description

OCRReader is inspired by classic commercial OCR software like ABBYY FineReader and OmniPage, but it is designed to be free and open-source. This is a personal project that evolved from my need to OCR complex documents with Tesseract OCR like old game magazines that often have multiple columns, images, and text in different sizes and colors, and always need manual corrections, with a main issue being hyphenation and text flow over multiple columns.

This software is *not* intended as a "fire and forget" OCR tool for automatic OCR of simple documents, but as a tool to prepare and OCR complex documents with manual corrections, and its goal is to make the process as fast and efficient as possible.

## Usage

Here are the typical steps to OCR a document with OCRReader:

1. Import images files (PNG, JPG, etc.) or PDF files.
2. Use the analysis functions to detect text areas, columns or draw regions manually using the box editor.
   1. Correct text areas, columns, and regions if needed.
   2. Set properties for each region like box type, or custom tags (that will later be used for exporting), or text flow.
3. OCR the document using the Tesseract OCR backend.
4. Correct the OCR results using the text editor.
5. Export the OCR results to a text file or HTML after checking the export preview.

OCRReader is designed to be fast and efficient, with a focus on keyboard shortcuts and a clean and simple user interface. It is designed to be used with a mouse and keyboard. It is not optimized for touchscreens.

## Features
 - Import images and PDF files.
 - Sophisticated box editor to draw and manipulate text areas, columns, and regions, including reordering and merging boxes.
 - Analysis functions to detect text areas, columns, and draw regions manually and semi-automatically.
 - customizable shortcuts for box types and custom classes.
 - Export to text files, HTML, and EPUB, utilizing custom tags and text flow.
  
## Roadmap

The software is still in early development, and many features are still missing, incomplete, or buggy. This is a one-person project, and I am working on it in my free time, and mostly implement features I need in my workflow for current projects (OCR of old game magazines for export to EPUB).

Some general features I plan to implement in the future or general improvements are:

 - Fix memory leaks.
 - Implement undo/redo.
 - Improve the Page Icon View.
 - General usability improvements.
 - Get more exports working (only preview and simple HTML export is implemented for now).