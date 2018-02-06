//
//  NewVitalsController.swift
//  xcPetalV3
//
//  Created by Bhai Jaiveer Singh on 10/23/17.
//  Copyright © 2017 Okavango Systems. All rights reserved.
//

import UIKit
import AWSIoT
import SwiftyJSON

class SantiGrowController: UIViewController {
    
    let thingName = "pi5"
    var celcius = false
    
    @IBOutlet weak var temperatureSPDisplay: UILabel!
    @IBOutlet weak var temperatureDisplay: UILabel!
    @IBOutlet weak var humidityDisplay: UILabel!
    @IBOutlet weak var autoButton: UISwitch!
    @IBOutlet weak var inOutButton: UISwitch!
    @IBOutlet weak var heatSwitch: UISwitch!
    @IBOutlet weak var lightButton: UISwitch!
    @IBOutlet weak var rangeLabel: UILabel!
    @IBOutlet weak var rangeStepper: UIStepper!
 
    var temperatureSPDisplayValue: Double {
        get {
            return Double(temperatureSPDisplay.text!)!
        }
        set {
            var roundedValue = Int(newValue.rounded())
            if celcius {
                roundedValue = Int(Double(roundedValue-32)/1.8)
            }
            temperatureSPDisplay.text = "SP: \(roundedValue)°"
        }
    }
    
    var temperatureDisplayValue: Double {
        get {
            return Double(temperatureDisplay.text!)!
        }
        set {
            var roundedValue = Int(newValue.rounded())
            if celcius {
                roundedValue = Int(Double(roundedValue-32)/1.8)
            }
            temperatureDisplay.text = "\(roundedValue)°"
        }
    }
    
    var humidityDisplayValue: Double {
        get {
            return Double(humidityDisplay.text!)!
        }
        set {
            let roundedValue = Int(newValue.rounded())
            humidityDisplay.text = "\(roundedValue)%"
        }
    }
    
    var rangeLabelValue: Int {
        get {
            let str = rangeLabel.text!
            var x = str.substring(from: str.index(str.endIndex, offsetBy: -3))
            x = x.substring(to: x.index(x.endIndex, offsetBy: -1))
            x = x.trimmingCharacters(in: .whitespacesAndNewlines)
            return Int(x)!
        }
        set {
            rangeLabel.text = "Temp Range: +/- \(newValue)°"
        }
    }
    
    func update(payload: Data) {
        print("updating")
        DispatchQueue.main.async {
            let json = JSON(data: (payload as NSData!) as Data)
            if json["state"]["reported"] != nil {
                self.updateStatus(payload: json)
            }
        }
    }
    
    // TODO: change the subs to circ, heat insteas circ_heat
    
    func updateStatus(payload json: JSON) {
        print("updating status")
        if let temperatureSPReported = json["state"]["reported"]["tempSP"].double {
            temperatureSPDisplayValue = temperatureSPReported
        }
        if let humidityReported = json["state"]["reported"]["humidity"].double {
            humidityDisplayValue = humidityReported
        }
        if let temperatureReported = json["state"]["reported"]["temperature"].double {
            temperatureDisplayValue = temperatureReported
        }
        if let lightReported = json["state"]["reported"]["light"].int {
            lightButton.isOn = Bool(lightReported as NSNumber)
        }
        if let heatReported = json["state"]["reported"]["heat"].int {
            heatSwitch.isOn = Bool(heatReported as NSNumber)
        }
        if let inOutReported = json["state"]["reported"]["in_out"].int {
            inOutButton.isOn = Bool(inOutReported as NSNumber)
        }
        if let inReported = json["state"]["reported"]["fan"].int {
            inOutButton.isOn = Bool(inReported as NSNumber)
        }
        if let autoReported = json["state"]["reported"]["auto"].int {
            autoButton.isOn = Bool(autoReported as NSNumber)
            heatSwitch.isEnabled = !autoButton.isOn
            inOutButton.isEnabled = !autoButton.isOn
            lightButton.isEnabled = !autoButton.isOn
        }
        if let rangeReported = json["state"]["reported"]["buffer"].int {
            rangeStepper.value = Double(rangeReported)
            rangeLabelValue = rangeReported
        }
    }
    
    @IBAction func autoChanging(_ sender: UISwitch) {
        let val = sender.isOn ? 1 : 0
        sendDelta(onTopic: "auto", withValue: val)
        heatSwitch.isEnabled = !Bool(val as NSNumber)
        inOutButton.isEnabled = !Bool(val as NSNumber)
        lightButton.isEnabled = !Bool(val as NSNumber)
    }
    
    @IBAction func lightChanging(_ sender: UISwitch) {
        let roundedValue = sender.isOn ? 1 : 0
        sendDelta(onTopic: "light", withValue: roundedValue)
    }
    
    @IBAction func inOutChanging(_ sender: UISwitch) {
        let roundedValue = sender.isOn ? 1 : 0
        sendDelta(onTopic: "in_out", withValue: roundedValue)
    }
    
    @IBAction func heatChanging(_ sender: UISwitch) {
        let roundedValue = sender.isOn ? 1 : 0
        sendDelta(onTopic: "heat", withValue: roundedValue)
    }
    
    @IBAction func rangeStepperChanging(_ sender: UIStepper) {
        let buffer = Int(sender.value)
        rangeLabel.text = "Temp Range: +/- \(buffer)°"
        sendDelta(onTopic: "buffer", withValue: buffer)
    }
    
    func sendDelta(onTopic topic: String, withValue val: Int) {
        let iotDataManager = AWSIoTDataManager.default()
        iotDataManager.publishString("{\"state\": {\"desired\": {\"\(topic)\": \"\(val)\"}}}", onTopic: "$aws/things/\(thingName)/shadow/update", qoS: .messageDeliveryAttemptedAtLeastOnce)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        let iotDataManager = AWSIoTDataManager.default()
        setupTapGesture()
        iotDataManager.subscribe(toTopic: "$aws/things/\(thingName)/shadow/update/accepted", qoS: AWSIoTMQTTQoS.messageDeliveryAttemptedAtLeastOnce, messageCallback: self.update)
        iotDataManager.subscribe(toTopic: "$aws/things/\(thingName)/shadow/get/accepted", qoS: AWSIoTMQTTQoS.messageDeliveryAttemptedAtLeastOnce, messageCallback: self.update)
        getShadowOf(thingName)
    }
    
    func getShadowOf(_ thingName: String) {
        let iotDataManager = AWSIoTDataManager.default()
        iotDataManager.publishString("", onTopic: "$aws/things/\(thingName)/shadow/get", qoS: .messageDeliveryAttemptedAtLeastOnce)
    }
    
    fileprivate func setupTapGesture() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(hideKeyboard))
        view.addGestureRecognizer(tapGesture)
    }
    
    @objc fileprivate func hideKeyboard() {
        view.endEditing(true)
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
}

// UIColor Helper
extension UIColor {
    public convenience init?(hexString: String) {
        let r, g, b, a: CGFloat
        
        if hexString.hasPrefix("#") {
            let start = hexString.index(hexString.startIndex, offsetBy: 1)
            let hexColor = hexString.substring(from: start)
            
            if hexColor.characters.count == 8 {
                let scanner = Scanner(string: hexColor)
                var hexNumber: UInt64 = 0
                
                if scanner.scanHexInt64(&hexNumber) {
                    r = CGFloat((hexNumber & 0xff000000) >> 24) / 255
                    g = CGFloat((hexNumber & 0x00ff0000) >> 16) / 255
                    b = CGFloat((hexNumber & 0x0000ff00) >> 8) / 255
                    a = CGFloat(hexNumber & 0x000000ff) / 255
                    
                    self.init(red: r, green: g, blue: b, alpha: a)
                    return
                }
            }
        }
        return nil
    }
}

