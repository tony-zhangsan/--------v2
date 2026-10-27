import Foundation
import Vision
import AppKit

// 输出每行文字及其归一化框（Vision 坐标：原点左下）
let args = CommandLine.arguments
for path in args.dropFirst() {
    print("########## \(path) ##########")
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("ERROR")
        continue
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.usesLanguageCorrection = false
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do { try handler.perform([request]) } catch { print("ERROR"); continue }
    guard let obs = request.results else { continue }
    for o in obs {
        guard let top = o.topCandidates(1).first else { continue }
        let b = o.boundingBox
        // x, y_top(从顶部算), w, h 全部归一化
        let yTop = 1.0 - (b.origin.y + b.size.height)
        print(String(format: "%.4f\t%.4f\t%.4f\t%.4f\t%@", b.origin.x, yTop, b.size.width, b.size.height, top.string))
    }
    print("")
}
