# ARKit Integration Guide

## Overview

This guide covers integrating USDZ files with ARKit and iOS Quick Look for native AR experiences. Learn how to implement AR Quick Look in iOS apps, web deployment, and optimization strategies for maximum compatibility.

## iOS Quick Look Integration

### Basic Setup

**Required iOS Version:** iOS 12.0+  
**Required Frameworks:**
- `QuickLook.framework`
- `ARKit.framework` (automatic with Quick Look)

### Swift Implementation

```swift
import UIKit
import QuickLook

class ARViewController: UIViewController {
    
    // MARK: - AR Quick Look Integration
    
    func presentARQuickLook(for modelName: String) {
        guard let url = Bundle.main.url(forResource: modelName, withExtension: "usdz") else {
            print("USDZ file not found: \(modelName)")
            return
        }
        
        let previewController = QLPreviewController()
        previewController.dataSource = self
        previewController.delegate = self
        present(previewController, animated: true)
    }
}

// MARK: - QLPreviewControllerDataSource
extension ARViewController: QLPreviewControllerDataSource {
    
    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        return 1
    }
    
    func previewController(_ controller: QLPreviewController, previewItemAt index: Int) -> QLPreviewItem {
        return currentModelURL as QLPreviewItem
    }
}

// MARK: - QLPreviewControllerDelegate  
extension ARViewController: QLPreviewControllerDelegate {
    
    func previewControllerDidDismiss(_ controller: QLPreviewController) {
        // Handle dismissal if needed
        print("AR Quick Look dismissed")
    }
}
```

### Advanced AR Quick Look Features

```swift
// Custom AR Quick Look with options
func presentAdvancedARQuickLook(modelURL: URL, allowsContentScaling: Bool = true) {
    let previewController = QLPreviewController()
    previewController.dataSource = self
    previewController.delegate = self
    
    // iOS 13+ advanced options
    if #available(iOS 13.0, *) {
        previewController.currentPreviewItemIndex = 0
    }
    
    present(previewController, animated: true) {
        // Completion handler
        print("AR Quick Look presented")
    }
}

// Check AR availability
func isARAvailable() -> Bool {
    return ARWorldTrackingConfiguration.isSupported
}

// Custom AR session handling
func setupCustomARSession() {
    guard isARAvailable() else {
        print("AR not supported on this device")
        return
    }
    
    // Custom AR implementation with RealityKit
    // (Advanced usage beyond Quick Look)
}
```

## Web Integration

### HTML AR Quick Look

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AR Quick Look Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>AR Sticker Gallery</h1>
    
    <!-- Basic AR Quick Look Link -->
    <a href="models/sticker.usdz" rel="ar">
        <img src="thumbnails/sticker.jpg" alt="AR Sticker">
        <p>View in AR</p>
    </a>
    
    <!-- Advanced AR Quick Look with fallback -->
    <a href="models/character.usdz" rel="ar">
        <img src="thumbnails/character.jpg" alt="3D Character">
        <p>Tap to view in AR</p>
    </a>
    
    <!-- iOS detection script -->
    <script>
        // Check if device supports AR
        if (navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')) {
            // Show AR-enabled content
            document.querySelectorAll('[rel="ar"]').forEach(link => {
                link.style.display = 'block';
            });
        } else {
            // Show fallback content
            document.querySelectorAll('[rel="ar"]').forEach(link => {
                link.href = link.href.replace('.usdz', '.png');
                link.removeAttribute('rel');
            });
        }
    </script>
</body>
</html>
```

### Advanced Web Integration

```html
<!-- Progressive enhancement for AR -->
<div class="ar-container">
    <a href="models/product.usdz" 
       rel="ar" 
       id="ar-link">
        <img src="thumbnails/product.jpg" 
             alt="Product Preview"
             id="product-image">
        <div class="ar-badge">View in AR</div>
    </a>
</div>

<script>
// Enhanced AR detection and analytics
function setupARExperience() {
    const arLinks = document.querySelectorAll('a[rel="ar"]');
    
    arLinks.forEach(link => {
        // Add click tracking
        link.addEventListener('click', function(e) {
            // Analytics tracking
            gtag('event', 'ar_view', {
                'custom_parameter': 'usdz_file_opened'
            });
            
            // iOS detection
            if (!isIOSDevice()) {
                e.preventDefault();
                showARNotSupportedMessage();
            }
        });
        
        // Preload USDZ files
        preloadUSDZ(link.href);
    });
}

function isIOSDevice() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

function preloadUSDZ(url) {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
}

function showARNotSupportedMessage() {
    alert('AR Quick Look is only supported on iOS devices with iOS 12 or later.');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', setupARExperience);
</script>
```

## RealityKit Integration

### Custom AR Experiences

```swift
import RealityKit
import ARKit
import Combine

class CustomARView: ARView {
    
    private var cancellables: Set<AnyCancellable> = []
    
    override func awakeFromNib() {
        super.awakeFromNib()
        setupARSession()
        loadUSDZModel()
    }
    
    private func setupARSession() {
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal, .vertical]
        config.environmentTexturing = .automatic
        
        if ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) {
            config.sceneReconstruction = .mesh
        }
        
        session.run(config)
    }
    
    private func loadUSDZModel() {
        // Load USDZ model with RealityKit
        guard let modelURL = Bundle.main.url(forResource: "sticker", withExtension: "usdz") else {
            print("USDZ model not found")
            return
        }
        
        Entity.loadModelAsync(contentsOf: modelURL)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to load model: \(error)")
                    }
                },
                receiveValue: { [weak self] modelEntity in
                    self?.placeModel(modelEntity)
                }
            )
            .store(in: &cancellables)
    }
    
    private func placeModel(_ modelEntity: ModelEntity) {
        // Create anchor
        let anchor = AnchorEntity(plane: .horizontal)
        
        // Scale model appropriately
        modelEntity.scale = [0.1, 0.1, 0.1]
        
        // Add to anchor
        anchor.addChild(modelEntity)
        
        // Add to scene
        scene.addAnchor(anchor)
        
        // Add tap gesture for interaction
        installGestures(.all, for: modelEntity)
    }
}
```

### Advanced RealityKit Features

```swift
// Animation support
extension CustomARView {
    
    func addAnimationToModel(_ modelEntity: ModelEntity) {
        // Rotation animation
        let rotationAnimation = FromToByAnimation<Transform>(
            name: "rotation",
            from: .identity,
            to: Transform(rotation: simd_quatf(angle: .pi * 2, axis: [0, 1, 0])),
            duration: 4.0,
            timing: .easeInOut,
            isAdditive: false
        )
        
        // Apply animation
        let animationResource = try! AnimationResource.generate(with: rotationAnimation)
        modelEntity.playAnimation(animationResource.repeat())
    }
    
    func addPhysicsToModel(_ modelEntity: ModelEntity) {
        // Add collision component
        let collisionComponent = CollisionComponent(
            shapes: [.generateBox(size: modelEntity.visualBounds(relativeTo: nil).extents)],
            mode: .trigger,
            filter: .sensor
        )
        modelEntity.components.set(collisionComponent)
        
        // Add physics body
        let physicsBody = PhysicsBodyComponent(
            massProperties: .default,
            material: .default,
            mode: .dynamic
        )
        modelEntity.components.set(physicsBody)
    }
}
```

## Platform-Specific Optimizations

### iOS Device Capabilities

```swift
// Device capability detection
extension UIDevice {
    
    var supportsLiDAR: Bool {
        if #available(iOS 14.0, *) {
            return ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh)
        }
        return false
    }
    
    var arPerformanceLevel: ARPerformanceLevel {
        // Determine device AR performance
        let modelName = UIDevice.current.model
        let systemVersion = UIDevice.current.systemVersion
        
        if modelName.contains("Pro") || modelName.contains("Pro Max") {
            return .high
        } else if modelName.contains("iPhone") && systemVersion.compare("13.0", options: .numeric) != .orderedAscending {
            return .medium
        } else {
            return .low
        }
    }
}

enum ARPerformanceLevel {
    case low, medium, high
    
    var maxVertexCount: Int {
        switch self {
        case .low: return 10000
        case .medium: return 25000
        case .high: return 50000
        }
    }
    
    var maxTextureSize: Int {
        switch self {
        case .low: return 512
        case .medium: return 1024
        case .high: return 2048
        }
    }
}
```

### Performance Optimization

```swift
// AR session optimization
class OptimizedARSession {
    
    func optimizeForDevice() {
        let device = UIDevice.current
        let config = ARWorldTrackingConfiguration()
        
        // Adjust configuration based on device capabilities
        switch device.arPerformanceLevel {
        case .low:
            config.videoFormat = ARWorldTrackingConfiguration.supportedVideoFormats.first!
            config.planeDetection = [.horizontal]
            
        case .medium:
            config.planeDetection = [.horizontal, .vertical]
            config.environmentTexturing = .automatic
            
        case .high:
            config.planeDetection = [.horizontal, .vertical]
            config.environmentTexturing = .automatic
            if ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) {
                config.sceneReconstruction = .mesh
            }
        }
    }
    
    func optimizeModelForAR(_ modelEntity: ModelEntity, targetVertexCount: Int) {
        // Model optimization logic
        // This would typically involve LOD management
        
        let currentVertexCount = getVertexCount(modelEntity)
        if currentVertexCount > targetVertexCount {
            // Apply mesh decimation or use lower LOD
            applyLODReduction(modelEntity, targetCount: targetVertexCount)
        }
    }
    
    private func getVertexCount(_ modelEntity: ModelEntity) -> Int {
        // Implementation to count vertices
        return 0 // Placeholder
    }
    
    private func applyLODReduction(_ modelEntity: ModelEntity, targetCount: Int) {
        // Implementation for LOD reduction
    }
}
```

## Distribution and Sharing

### File Sharing Integration

```swift
// Share USDZ files
extension UIViewController {
    
    func shareUSDZFile(url: URL) {
        let activityViewController = UIActivityViewController(
            activityItems: [url],
            applicationActivities: nil
        )
        
        // iPad support
        if let popover = activityViewController.popoverPresentationController {
            popover.sourceView = view
            popover.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.midY, width: 0, height: 0)
            popover.permittedArrowDirections = []
        }
        
        present(activityViewController, animated: true)
    }
    
    func exportUSDZToFiles(url: URL) {
        // Export to Files app
        let documentPicker = UIDocumentPickerViewController(forExporting: [url])
        documentPicker.delegate = self
        present(documentPicker, animated: true)
    }
}

extension UIViewController: UIDocumentPickerDelegate {
    
    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        // Handle successful export
        print("USDZ exported successfully")
    }
}
```

### URL Schemes and Deep Linking

```swift
// Handle USDZ deep links
func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    
    if url.pathExtension.lowercased() == "usdz" {
        // Handle USDZ file
        presentARQuickLook(for: url)
        return true
    }
    
    return false
}

func presentARQuickLook(for url: URL) {
    guard let topViewController = getTopViewController() else { return }
    
    let previewController = QLPreviewController()
    previewController.dataSource = ARQuickLookDataSource(url: url)
    topViewController.present(previewController, animated: true)
}

class ARQuickLookDataSource: NSObject, QLPreviewControllerDataSource {
    private let url: URL
    
    init(url: URL) {
        self.url = url
    }
    
    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        return 1
    }
    
    func previewController(_ controller: QLPreviewController, previewItemAt index: Int) -> QLPreviewItem {
        return url as QLPreviewItem
    }
}
```

## Testing and Debugging

### AR Quick Look Testing

```swift
// Testing utilities
class ARQuickLookTester {
    
    static func validateUSDZFile(at url: URL) -> ValidationResult {
        var result = ValidationResult()
        
        // Check file exists
        result.fileExists = FileManager.default.fileExists(atPath: url.path)
        
        // Check file size
        do {
            let attributes = try FileManager.default.attributesOfItem(atPath: url.path)
            let fileSize = attributes[.size] as? Int64 ?? 0
            result.fileSize = fileSize
            result.sizeValid = fileSize < 25 * 1024 * 1024 // 25MB limit
        } catch {
            result.error = error
        }
        
        // Check USDZ validity
        result.isValidUSDZ = isValidUSDZFile(url)
        
        return result
    }
    
    private static func isValidUSDZFile(_ url: URL) -> Bool {
        // Basic validation - check if it's a valid zip with USD content
        // This is a simplified check
        return url.pathExtension.lowercased() == "usdz"
    }
}

struct ValidationResult {
    var fileExists: Bool = false
    var fileSize: Int64 = 0
    var sizeValid: Bool = false
    var isValidUSDZ: Bool = false
    var error: Error?
    
    var isValid: Bool {
        return fileExists && sizeValid && isValidUSDZ && error == nil
    }
}
```

### Debug Information

```swift
// AR debugging utilities
extension ARView {
    
    func enableARDebugging() {
        // Show feature points
        debugOptions.insert(.showFeaturePoints)
        
        // Show world origin
        debugOptions.insert(.showWorldOrigin)
        
        // Show anchor origins
        debugOptions.insert(.showAnchorOrigins)
        
        // Show anchor geometry
        debugOptions.insert(.showAnchorGeometry)
    }
    
    func logARSessionInfo() {
        guard let frame = session.currentFrame else { return }
        
        print("AR Session Info:")
        print("- Camera transform: \(frame.camera.transform)")
        print("- Tracking state: \(frame.camera.trackingState)")
        print("- Anchors count: \(frame.anchors.count)")
        print("- Feature points: \(frame.rawFeaturePoints?.points.count ?? 0)")
    }
}
```

## Best Practices

### Performance Guidelines

1. **File Size Limits:**
   - Keep USDZ files under 25MB for Quick Look
   - Optimize textures to 1024×1024 or smaller
   - Use compressed texture formats when possible

2. **Geometry Optimization:**
   - Target <25K vertices for mobile devices
   - Use LOD (Level of Detail) systems
   - Optimize UV layouts for texture atlasing

3. **Material Efficiency:**
   - Limit to 5-10 materials per model
   - Use PBR materials for realistic rendering
   - Avoid complex shader networks

### User Experience

1. **Clear AR Indicators:**
   - Use AR badges/icons for AR-enabled content
   - Provide fallback for non-AR devices
   - Show loading states for large files

2. **Intuitive Interactions:**
   - Support standard AR gestures (tap, pinch, rotate)
   - Provide clear placement instructions
   - Include reset/recenter options

3. **Accessibility:**
   - Support VoiceOver for AR content
   - Provide alternative text descriptions
   - Include keyboard navigation options

## Resources and References

### Apple Documentation
- [AR Quick Look Developer Guide](https://developer.apple.com/augmented-reality/quick-look/)
- [ARKit Documentation](https://developer.apple.com/documentation/arkit/)
- [RealityKit Documentation](https://developer.apple.com/documentation/realitykit/)
- [Quick Look Framework](https://developer.apple.com/documentation/quicklook/)

### Tools and Utilities
- **Reality Converter** - Convert 3D models to USDZ
- **Reality Composer** - Create AR experiences
- **Xcode usdz_converter** - Command line USDZ conversion
- **USD Python API** - Programmatic USDZ creation

### Sample Code
- [Apple AR Quick Look Sample](https://developer.apple.com/documentation/arkit/previewing-a-model-with-ar-quick-look)
- [RealityKit Samples](https://developer.apple.com/augmented-reality/reality-kit/)

### Community Resources
- [Apple Developer Forums - ARKit](https://developer.apple.com/forums/tags/arkit)
- [OpenUSD Community](https://openusd.org/release/index.html)
- [ARKit by Example](https://github.com/hanleyweng/ARKit-by-Example)

## Next Steps

1. **Advanced AR Features Guide** - Animations, physics, interactions
2. **Cross-Platform AR Guide** - Android ARCore, WebXR compatibility  
3. **Material and Shader Guide** - Advanced PBR materials for AR
4. **Performance Optimization Guide** - Mobile AR performance tuning
