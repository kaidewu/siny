import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import { NativeTypes } from 'react-dnd-html5-backend';

interface DragAndDropProps {
  onDrop: (files: FileList) => void;
}

const DragAndDrop: React.FC<DragAndDropProps> = ({ onDrop }) => {
  const [droppedFile, setDroppedFile] = useState<File | null>(null);
  const [{ canDrop, isOver }, drop] = useDrop(() => ({
    accept: [NativeTypes.FILE],
    drop: (item: { files: FileList }) => {
      const file = item.files[0];
      setDroppedFile(file);
      onDrop(item.files);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  return (
    <div
      ref={drop}
      className={`border-2 border-dashed p-8 text-center ${canDrop && isOver ? 'bg-gray-100' : 'bg-white'}`}
    >
      {droppedFile ? (
        <div>
          <p className="text-green-600 font-semibold">File dropped:</p>
          <p className="text-gray-800">{droppedFile.name}</p>
        </div>
      ) : (
        canDrop && isOver ? 'Release to drop' : 'Drag and drop files here'
      )}
    </div>
  );
};

export default DragAndDrop;
