//
//  ScheduleViewController.swift
//  xcPetalV3
//
//  Created by Bhai Jaiveer Singh on 12/12/17.
//  Copyright © 2017 Okavango Systems. All rights reserved.
//

import UIKit
import AWSIoT
import SwiftyJSON

class ScheduleViewController: UIViewController {
    
    let thingName = "pi5"
    let iotDataManager = AWSIoTDataManager.default()
    let userDefaults = UserDefaults.standard
    
    @IBOutlet weak var dayTemp: UITextField!
    @IBOutlet weak var dayStart: UITextField!
    @IBOutlet weak var nightTemp: UITextField!
    @IBOutlet weak var nightStart: UITextField!
    
    @IBAction func dayTempChanged(_ sender: UITextField) {
        userDefaults.set(dayTemp.text!, forKey: "dayTemp")
        let profile = "{'name': 'day', 'temperatureSP': \(dayTemp.text!), 'humiditySP': 60, 'light': 1, 'blue': 0}"
        iotDataManager.publishString(_: profile, onTopic: "\(thingName)/profile", qoS: .messageDeliveryAttemptedAtLeastOnce)
    }
    
    @IBAction func nightTempChanged(_ sender: UITextField) {
        userDefaults.set(nightTemp.text!, forKey: "nightTemp")
        let profile = "{'name': 'night', 'temperatureSP': \(nightTemp.text!), 'humiditySP': 60, 'light': 0, 'blue': 0}"
        iotDataManager.publishString(_: profile, onTopic: "\(thingName)/profile", qoS: .messageDeliveryAttemptedAtLeastOnce)
    }
    
    @IBAction func scheduleChanged(_ sender: UITextField) {
        userDefaults.set(dayStart.text!, forKey: "dayStart")
        userDefaults.set(nightStart.text!, forKey: "nightStart")
        let schedule = "[['day','\(dayStart.text!)'],['night','\(nightStart.text!)']]"
        iotDataManager.publishString(_: schedule, onTopic: "\(thingName)/schedule", qoS: .messageDeliveryAttemptedAtLeastOnce)
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
    
    func updateStatus(payload json: JSON) {
        print("updating status")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        iotDataManager.subscribe(toTopic: "$aws/things/\(thingName)/shadow/update/accepted", qoS: AWSIoTMQTTQoS.messageDeliveryAttemptedAtLeastOnce, messageCallback: self.update)
        iotDataManager.subscribe(toTopic: "$aws/things/\(thingName)/shadow/get/accepted", qoS: AWSIoTMQTTQoS.messageDeliveryAttemptedAtLeastOnce, messageCallback: self.update)
        getShadowOf(thingName)
        dayTemp.text = userDefaults.string(forKey: "dayTemp")
        nightTemp.text = userDefaults.string(forKey: "nightTemp")
        dayStart.text = userDefaults.string(forKey: "dayStart")
        nightStart.text = userDefaults.string(forKey: "nightStart")
    }
    func getShadowOf(_ thingName: String) {
        let iotDataManager = AWSIoTDataManager.default()
        iotDataManager.publishString("", onTopic: "$aws/things/\(thingName)/shadow/get", qoS: .messageDeliveryAttemptedAtLeastOnce)
    }
}
