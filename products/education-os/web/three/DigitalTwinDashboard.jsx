import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";

function Room({position,label}) {
  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={[3,1.5,3]} />
        <meshStandardMaterial />
      </mesh>
      <Text position={[0,1.2,0]} fontSize={0.25}>
        {label}
      </Text>
    </group>
  );
}

export default function DigitalTwinDashboard() {
  return (
    <Canvas camera={{position:[8,6,8]}}>
      <ambientLight intensity={1}/>
      <directionalLight position={[5,5,5]}/>

      <Room position={[-3,0,0]} label="Classrooms"/>
      <Room position={[0,0,0]} label="Director Office"/>
      <Room position={[3,0,0]} label="Finance"/>
      <Room position={[0,0,-3]} label="Parent Portal"/>

      <Text position={[0,2,0]} fontSize={0.4}>
        Little Oaks 3D Command Center
      </Text>

      <OrbitControls/>
    </Canvas>
  );
}
