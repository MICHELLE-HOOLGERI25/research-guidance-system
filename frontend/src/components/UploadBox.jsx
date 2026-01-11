export default function UploadBox({ onUpload }) {
  return (
    <input
      type="file"
      accept=".pdf"
      onChange={(e) => onUpload(e.target.files[0])}
    />
  );
}
