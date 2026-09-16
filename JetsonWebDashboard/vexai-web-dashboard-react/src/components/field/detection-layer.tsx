import React, { useEffect, useState } from "react";
import { Layer, Image } from "react-konva";
import { config } from "../../util/config";
import { useAppSelector } from "../../state/hooks";
import { Element } from "../../lib/types";
import { v4 as uuidv4 } from "uuid";

interface DetectionLayerProps {
  fieldWidth: number;
  fieldHeight: number;
}

// All Override element classes, in Element enum order (see lib/types.ts / JetsonExample/labels.txt).
const ELEMENT_CLASSES = Object.values(Element).filter(
  (value) => typeof value === "number"
) as Element[];

/**
 * Loads one image per detectable element class up front. Kept as a single hook (rather
 * than calling an image-loading hook once per class in a loop) so the number of hooks
 * called stays constant across renders.
 */
const useElementImages = (): Partial<Record<Element, HTMLImageElement>> => {
  const [loaded, setLoaded] = useState<Partial<Record<Element, HTMLImageElement>>>({});

  useEffect(() => {
    let cancelled = false;
    ELEMENT_CLASSES.forEach((elementClass) => {
      const img = new window.Image();
      img.src = config.elements.textures[elementClass];
      img.onload = () => {
        if (!cancelled) {
          setLoaded((prev) => ({ ...prev, [elementClass]: img }));
        }
      };
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return loaded;
};

/**
 * Displays elements on the field detected by the robot
 *
 * @param param0 Detection layer properties
 * @returns JSX.Element
 */
const DetectionLayer = ({ fieldWidth, fieldHeight }: DetectionLayerProps) => {
  const detections = useAppSelector((state) => state.data.response.detections);
  const scale = useAppSelector((state) => state.app.scale);
  const elementImages = useElementImages();

  const getImage = (detectionClass: number) => elementImages[detectionClass as Element];

  return (
    <Layer>
      {detections ? (
        <>
          {detections.map((detection) => {
            const widthScale = scale * config.elements.size[detection.class].width * config.elements.size[detection.class].scale;
            const heightScale = scale * config.elements.size[detection.class].height * config.elements.size[detection.class].scale;
            return (
              <>
                {detection.depth !== -1 ? (
                  <Image
                    key={`${
                      config.elements.label.text[detection.class]
                    }-${uuidv4()}`}
                    alt=""
                    image={getImage(detection.class)}
                    x={detection.mapLocation.x[0] * scale * config.elements.size[detection.class].scale}
                    y={detection.mapLocation.y[0] * scale * -1 * config.elements.size[detection.class].scale}
                    z={detection.depth}
                    width={widthScale}
                    height={heightScale}
                    offsetX={widthScale / 2}
                    offsetY={widthScale / 2}
                  />
                ) : null}
              </>
            );
          })}
        </>
      ) : null}
    </Layer>
  );
};

export default DetectionLayer;
