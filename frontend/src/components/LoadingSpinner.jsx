export default function LoadingSpinner({ text = "Analyzing..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-4 border-gray-200" />
        <div className="absolute inset-0 w-12 h-12 rounded-full border-4 border-transparent border-t-airbnb animate-spin" />
      </div>
      <p className="text-gray-airbnb font-medium">{text}</p>
    </div>
  );
}
